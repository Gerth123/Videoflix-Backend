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
from django.shortcuts import render, redirect
from video_app.models import Video
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


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

    def send_activation_email(self, user_email, user_name, activation_url):
        subject = "Confirm your email"
        from_email = "robingerth21@gmail.com"
        recipient_list = [user_email]

        text_content = f"Hello {user_name},\n\nClick the following link to activate your account: {activation_url}\n\nBest regards,\nYour Videoflix Team"
        html_content = render_to_string("emails/activation_email.html", {
            "user_name": user_name,
            "activation_url": activation_url,
            "site_url": settings.SITE_URL
        })

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = get_unique_username(email)

            saved_account = User.objects.create_user(
                username=username,
                email=email,
                password=serializer.validated_data['password'],
                is_active=False,
            )

            user_profile, created = UserProfile.objects.get_or_create(user=saved_account, defaults={'email_sent': False})

            token = default_token_generator.make_token(saved_account)
            uid = urlsafe_base64_encode(force_bytes(saved_account.pk))

            activation_url = f"{settings.SITE_URL}{reverse('activate-account', kwargs={'uidb64': uid, 'token': token})}"

            try:
                self.send_activation_email(saved_account.email, saved_account.username, activation_url)
                user_profile.email_sent = True
                user_profile.save()
            except Exception:
                return Response({"error": "E-Mail-Versand fehlgeschlagen."}, status=500)

            return Response({
                'username': saved_account.username,
                'email': saved_account.email,
                'toast_message': "Bitte prüfe dein E-Mail-Postfach und klicke auf den Aktivierungslink."
            })

        return Response(serializer.errors)

def get_unique_username(email):
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                return Response({
                    'token': token_obj.key,
                    'email': user.email,
                    'user_id': user.id,
                    'is_active': user.is_active
                })
            except Token.DoesNotExist:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'email': user.email,
                        'user_id': user.id,
                        'is_active': user.is_active
                    })
                else:
                    return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'No token or email/password provided'}, status=status.HTTP_400_BAD_REQUEST)

    
class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            user_profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, ValueError):
            return redirect(f"{settings.FRONTEND_URL}/activation-failed/")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user_profile.is_active = True
            user.save()
            user_profile.save()
            return redirect(f"{settings.FRONTEND_URL}/account-confirmed/")
        else:
            return redirect(f"{settings.FRONTEND_URL}/activation-failed/")
        
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                token = get_random_string(50)  
                cache.set(f"password_reset_{token}", user.id, timeout=3600)  
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

                send_mail(
                    "Passwort zurücksetzen",
                    f"Klicke hier, um dein Passwort zurückzusetzen: {reset_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

            return Response({"message": "Falls die E-Mail existiert, wurde eine Nachricht gesendet."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['password']
            
            user_id = cache.get(f"password_reset_{token}")
            if not user_id:
                return Response({"error": "Token ist ungültig oder abgelaufen."}, status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_404(User, id=user_id)
            user.set_password(new_password)
            user.save()
            cache.delete(f"password_reset_{token}")

            return Response({"message": "Passwort erfolgreich geändert."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

