"""
Account URL configuration.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("style-profile/", views.StyleProfileView.as_view(), name="style-profile"),
    path("addresses/", views.AddressListCreateView.as_view(), name="address-list"),
    path("addresses/<uuid:pk>/", views.AddressDetailView.as_view(), name="address-detail"),
]
