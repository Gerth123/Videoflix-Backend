from django.conf import settings
from rest_framework import generics
from users_app.models import UserProfile
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from video_app.models import Video
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator



CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

#Backend Modul 10 - Video 09 Redis Caching. Daten vorlade, bzw im Arbeitsspeicher belassen.
@cache_page(CACHE_TTL)
def index(request):
    videos = Video.objects.all()
    return render(request, 'index.html', {'videos': videos})    

class UserProfileList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer    

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            base_username = email.split('@')[0]
            username = base_username

            # Prüfen, ob der Benutzername bereits existiert
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Benutzerobjekt manuell erstellen, da serializer.save() username nicht erwartet
            saved_account = User.objects.create_user(
                username=username,
                email=email,
                password=serializer.validated_data['password'],
                is_active=False,
            )

            user_profile, created = UserProfile.objects.get_or_create(user=saved_account)
            user_profile.email_sent = False 
            user_profile.save()

            token = default_token_generator.make_token(saved_account)
            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))

            activation_url = request.build_absolute_uri(
                reverse("activate-account", kwargs={"uidb64": uid, "token": token})
            )

            send_mail(
                subject="Bestätige deinen Account",
                message=f"Klicke auf den folgenden Link, um deinen Account zu aktivieren: {activation_url}",
                from_email="robingerth21@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )

            user_profile.email_sent = True
            user_profile.save()            
            
            toast_message = f"Bitte prüfe dein E-Mail-Postfach und klicke auf den Aktivierungslink, um dein Konto zu aktivieren."

            return Response({
                'username': saved_account.username,
                'email': saved_account.email,
                'toast_message': toast_message
            })
        
        return Response(serializer.errors)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')

        if token:
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                return Response({
                    'token': token_obj.key,
                    # 'username': user.username,
                    'email': user.email,
                    'user_id': user.id
                })
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmailAuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                # 'username': user.username,
                'email': user.email,
                'user_id': user.id
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            user_profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Ungültiger Aktivierungslink"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user_profile.is_active = True
            user.save()
            user_profile.save()
            return Response({"message": "Dein Account wurde aktiviert! Du kannst dich nun einloggen."})
        else:
            return Response({"error": "Token ist ungültig oder abgelaufen"}, status=400)

