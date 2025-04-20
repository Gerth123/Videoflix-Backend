from django.conf import settings
from rest_framework import generics
from users_app.models import UserProfile
from .serializers import (
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    RegistrationSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect
from video_app.models import Video
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import format_html
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


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
        """
        Sends an activation email to the user.

        This function composes and sends an email to the user
        containing a link to activate their account. The email
        is sent in both plain text and HTML formats.

        Args:
            user_email (str): The email address of the recipient.
            user_name (str): The name of the user to personalize the email.
            activation_url (str): The URL for the user to activate their account.

        """
        subject = "Confirm your email"
        from_email = "robingerth21@gmail.com"
        recipient_list = [user_email]
        text_content = (
            f"Hello {user_name},\n\nClick the following link to activate your account: "
            f"{activation_url}\n\nBest regards,\nYour Videoflix Team"
        )
        html_content = render_to_string("emails/activation_email.html", {
            "user_name": user_name,
            "activation_url": activation_url,
            "site_url": settings.SITE_URL
        })
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def post(self, request):
        """
        Handles the registration of a new user.

        This function receives a POST request with the new user's email and password.
        If the data is valid, it creates a new inactive user account, a new user profile
        and sends an activation email to the user.
        If the email sending fails, it returns a 500 Internal Server Error with an
        appropriate error message.
        If everything goes well, it returns a success response with the username and
        email of the new user, as well as a toast message to be displayed to the user.

        Returns:
            Response: A success response with the username, email and a toast message, or
            a 500 Internal Server Error response with an appropriate error message.
        """
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        user = self.create_inactive_user(serializer)
        user_profile = self.get_or_create_user_profile(user)
        activation_url = self.build_activation_url(user)

        try:
            self.send_activation_email(user.email, user.username, activation_url)
            user_profile.email_sent = True
            user_profile.save()
        except Exception:
            return Response({"error": "E-Mail-Versand fehlgeschlagen."}, status=500)

        return Response({
            'username': user.username,
            'email': user.email,
            'toast_message': "Bitte prüfe dein E-Mail-Postfach und klicke auf den Aktivierungslink."
        })

    def create_inactive_user(self, serializer):
        """
        Creates an inactive user account with the given email and password.

        This function creates a new inactive user account with the given email and
        password. The username of the new user is generated as a random string
        based on the given email.

        Args:
            serializer (RegistrationSerializer): The serializer containing the
                email and password data.

        Returns:
            User: The newly created user object.
        """
        email = serializer.validated_data['email']
        username = get_unique_username(email)
        return User.objects.create_user(
            username=username,
            email=email,
            password=serializer.validated_data['password'],
            is_active=False,
        )

    def get_or_create_user_profile(self, user):
        """
        Retrieve or create a user profile for the given user.

        Args:
            user (User): The user for whom to retrieve or create a UserProfile.
        Returns:
            UserProfile: The retrieved or newly created UserProfile instance.
        """
        return UserProfile.objects.get_or_create(user=user, defaults={'email_sent': False})[0]

    def build_activation_url(self, user):
        """
        Builds an activation URL for the given user.

        Args:
            user (User): The user for whom to generate the activation URL.

        Returns:
            str: The activation URL for the user.
        """
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return f"{settings.SITE_URL}{reverse('activate-account', kwargs={'uidb64': uid, 'token': token})}"


def get_unique_username(email):
    """
    Generate a unique username based on the given email address.

    Args:
        email (str): The email address from which to generate the username.

    Returns:
        str: The unique username.
    """
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
        """
        Handles login with either a token or email/password.

        Args:
            request (Request): The request object containing the token or email/password.

        Returns:
            Response: A 200 OK response with the user data, or a 400 Bad Request response
            with an appropriate error message.
        """
        token = self.extract_token(request)
        if token:
            return self.login_with_token(token)

        email = request.data.get('email')
        password = request.data.get('password')
        if email and password:
            return self.login_with_credentials(email, password)

        return Response({'error': 'No token or email/password provided'}, status=status.HTTP_400_BAD_REQUEST)

    def extract_token(self, request):
        """
        Extracts the token from the Authorization header of the request, if present.

        Args:
            request (Request): The request object.

        Returns:
            str or None: The token if found, otherwise None.
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Token '):
            return auth_header.split(' ')[1]
        return None

    def login_with_token(self, token):
        """
        Logs in with a token, returning a 200 OK response with the user data.

        Args:
            token (str): The token to use for login.

        Returns:
            Response: A 200 OK response with the user data, or a 400 Bad Request response
            with an appropriate error message.
        """
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            return self.build_login_response(user, token_obj.key)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    def login_with_credentials(self, email, password):
        """
        Authenticates a user using email and password, returning a 200 OK response
        with the user data and token if successful.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            Response: A 200 OK response with the user data and token if authentication
            is successful, or a 400 Bad Request response with an error message if
            authentication fails.
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                return self.build_login_response(user, token.key)
        except User.DoesNotExist:
            pass
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

    def build_login_response(self, user, token_key):
        """
        Constructs a login response containing user information and authentication token.

        Args:
            user (User): The user object for which the response is being generated.
            token_key (str): The authentication token key associated with the user.

        Returns:
            Response: A Response object containing the user's token, email, user ID, and
            activation status.
        """
        return Response({
            'token': token_key,
            'email': user.email,
            'user_id': user.id,
            'is_active': user.is_active
        })


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """
        Handles the GET request to activate a user's account.

        Args:
            request (Request): The request object containing the activation token.
            uidb64 (str): The user's ID base64-encoded.
            token (str): The activation token.

        Returns:
            Response: A redirect to either the account confirmed or activation failed
            page, depending on whether the activation was successful.
        """
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
        """
        Handles the POST request to reset a user's password.

        Args:
            request (Request): The request object containing the email.

        Returns:
            Response: A success response with a message indicating that an email has
            been sent if the email exists.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            self.send_password_reset_email(user)

        return Response({"message": "Falls die E-Mail existiert, wurde eine Nachricht gesendet."})

    def send_password_reset_email(self, user):
        """
        Sends a password reset email to the user.

        Args:
            user (User): The user to send the email to.

        Returns:
            None
        """
        token = self.generate_and_cache_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Passwort zurücksetzen"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        text_content = f"Klicke auf den folgenden Link, um dein Passwort zurückzusetzen: {reset_url}"
        html_content = self.build_html_email(reset_url)
        email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

    def generate_and_cache_token(self, user):
        """
        Generates a random token and caches it for 1 hour, mapping it to the given user's ID.

        Args:
            user (User): The user to generate the token for.

        Returns:
            str: The generated token.
        """
        token = get_random_string(50)
        cache.set(f"password_reset_{token}", user.id, timeout=3600)
        return token

    def build_html_email(self, reset_url):
        """
        Builds an HTML email for the password reset email.

        Args:
            reset_url (str): The URL to reset the password.

        Returns:
            str: The generated HTML email.
        """
        return format_html(
            """
            <p>Klicke auf den Button unten, um dein Passwort zurückzusetzen:</p><br>
            <a href="{}" style="
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: white;
                background-color: #007bff;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;">
                Passwort zurücksetzen
            </a><br>
            <p>Falls du diese Anfrage nicht gestellt hast, ignoriere diese E-Mail.</p><br>
            <p>Vielen Dank, dass du bei Videoflix bist!</p>
            <p>Dein Videoflix Team</p>
            """, reset_url
        )


class PasswordResetConfirmView(APIView):
    def post(self, request):
        """
        Handles the POST request to reset a user's password.

        Args:
            request (Request): The request object containing the token and new
                password.

        Returns:
            Response: A success response with a message indicating that the
                password has been changed, or a 400 Bad Request response with an
                appropriate error message.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['password']
            user_id = cache.get(f"password_reset_{token}")
            if not user_id:
                return Response({"error": "Token ist ungültig oder"
                                 " abgelaufen."},
                                status=status.HTTP_400_BAD_REQUEST)
            user = get_object_or_404(User, id=user_id)
            user.set_password(new_password)
            user.save()
            cache.delete(f"password_reset_{token}")
            return Response({"message": "Passwort erfolgreich geändert."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
