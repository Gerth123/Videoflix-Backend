from django.contrib import admin
from .models import UserProfile
from rest_framework.authtoken.models import Token


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "slug", "get_is_staff",
                    "get_is_superuser", "get_token", "email_sent")
    search_field = ("user__email")
    list_filter = ("user__is_staff", "user__is_superuser")
    autocomplete_fields = ("user",)
    readonly_fields = ("slug",)
    fieldsets = (
        ("Benutzer-Informationen", {
            "fields": ("user", "slug")
        }),
    )

    def get_token(self, obj):
        """
        Retrieves the API token for the given user.

        Args:
            obj (UserProfile): The UserProfile object containing the user for whom to retrieve the token.

        Returns:
            str: The token key if it exists, otherwise "Kein Token".
        """
        token = Token.objects.filter(user=obj.user).first()
        return token.key if token else "Kein Token"

    get_token.short_description = "API Token"

    def get_is_staff(self, obj):
        """
        Determine if the user associated with the UserProfile is a staff member.

        Args:
            obj (UserProfile): The UserProfile object containing the user to check.

        Returns:
            bool: True if the user is a staff member, False otherwise.
        """
        return obj.user.is_staff
    get_is_staff.boolean = True
    get_is_staff.short_description = "Staff"

    def get_is_superuser(self, obj):
        """
        Determine if the user associated with the UserProfile is a superuser.

        Args:
            obj (UserProfile): The UserProfile object containing the user to check.

        Returns:
            bool: True if the user is a superuser, False otherwise.
        """
        return obj.user.is_superuser
    get_is_superuser.boolean = True
    get_is_superuser.short_description = "Superuser"
