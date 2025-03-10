from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):  
    list_display = ("user", "slug", "get_is_staff", "get_is_superuser")  
    search_fields = ("user__username", "phone")  
    list_filter = ("user__is_staff", "user__is_superuser")  
    autocomplete_fields = ("user",)  
    readonly_fields = ("slug",)  

    fieldsets = (
        ("Benutzer-Informationen", {
            "fields": ("user", "slug")
        }),
    )

    # Diese Methoden greifen auf das verknüpfte User-Modell zu
    def get_is_staff(self, obj):
        return obj.user.is_staff
    get_is_staff.boolean = True  # Zeigt ein Häkchen statt True/False
    get_is_staff.short_description = "Staff"

    def get_is_superuser(self, obj):
        return obj.user.is_superuser
    get_is_superuser.boolean = True
    get_is_superuser.short_description = "Superuser"
