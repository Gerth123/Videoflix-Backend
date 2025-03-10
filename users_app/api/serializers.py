from users_app.models import UserProfile
from rest_framework import serializers
from django.contrib.auth.models import User
from utils.validators import validate_no_html
from django.contrib.auth import authenticate


class UserProfileSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        exclude = ['user']


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, validators=[validate_no_html])
    email = serializers.CharField(
        max_length=100, validators=[validate_no_html])
    color = serializers.CharField(max_length=7, validators=[validate_no_html])

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'email', 'phone', 'color', 'contacts']


class RegistrationSerializer(serializers.Serializer):
    # username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self):
        '''
        Create and return a new user account.
        '''
        user = self.create_user()
        self.create_user_profile(user)
        return user

    def create_user(self):
        '''
        Create and return a new user account.
        '''
        password = self.validated_data['password']
        user = User(
            # username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        user.set_password(password)
        user.save()
        return user

    def create_user_profile(self, user):
        '''
        Create and return a new user profile.
        '''
        return UserProfile.objects.create(user=user)

class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        '''
        Validate the email and password.
        '''
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                # username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Benutzer mit dieser E-Mail existiert nicht.")
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Ungültige Anmeldedaten.")
        else:
            raise serializers.ValidationError(
                "E-Mail und Passwort sind erforderlich.")
        attrs['user'] = user
        return attrs
