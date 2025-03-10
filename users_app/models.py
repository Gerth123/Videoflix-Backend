from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # color = models.CharField(max_length=7)
    slug = models.SlugField(blank=True, default='')

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
        Generate a random color if no color is provided.
        '''
        if self.user.email:
            self.user.email = self.user.email.lower()
            self.user.save()
        
        if not self.slug:
            self.slug = slugify(self.user.email)

        super(UserProfile, self).save(*args, **kwargs)

