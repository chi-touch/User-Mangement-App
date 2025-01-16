from django.urls import path
from .views import RegisterView, LoginView, ProfileUpdateView,VerifyEmailView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/profile/', ProfileUpdateView.as_view(), name='profile-update'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),


]
