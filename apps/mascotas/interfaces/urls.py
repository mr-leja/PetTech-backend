from django.urls import path
from apps.mascotas.interfaces.views import MascotaListCreateView, MascotaDetailView

urlpatterns = [
    path('mascotas/', MascotaListCreateView.as_view(), name='mascotas-list'),
    path('mascotas/<int:pk>/', MascotaDetailView.as_view(), name='mascotas-detail'),
]
