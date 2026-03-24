from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.usuarios.interfaces.views import LoginView, RegistroView, PerfilView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/perfil/', PerfilView.as_view(), name='perfil'),
]
