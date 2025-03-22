from django.urls import path, include
from .views import CustomLoginView, RegisterPage,send_email,weather_view

from django.contrib.auth.views import LogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path('send_email',send_email,name='send_email'),
    path('weather_view',weather_view,name='weather_view'),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", RegisterPage.as_view(), name="register"),
    path("api/v1/", include("accounts.api.v1.urls")),
]
