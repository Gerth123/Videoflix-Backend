from django.contrib.auth.forms import UserCreationForm
from users_app.models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = '__all__'