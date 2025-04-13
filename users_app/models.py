from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, default='')
    is_active = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        '''
        Return the email of the user.
        '''
        return self.user.email

    def save(self, *args, **kwargs):
        '''
        Save the UserProfile instance. Also save the associated User instance
        if its email has been changed to lowercase. If the slug is empty, set it
        to the slugified version of the User's email address.
        Create a Token for the user if it does not already exist.
        '''
        if self.user.email:
            email_lower = self.user.email.lower()
            if self.user.email != email_lower:
                self.user.email = email_lower
                self.user.save(update_fields=["email"])
        if not self.slug:
            self.slug = slugify(self.user.email)

        super(UserProfile, self).save(*args, **kwargs)

        token, created = Token.objects.get_or_create(user=self.user)
