from django.urls import path
from .views import UserProfileList, UserProfileDetail, \
    RegistrationView, CustomLoginView, ActivateAccountView, \
    PasswordResetRequestView, PasswordResetConfirmView


urlpatterns = [     
    path('', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
