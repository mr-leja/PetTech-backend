from django.urls import path
from apps.adopciones.interfaces.views import (
    SolicitudAdopcionListCreateView,
    SolicitudAdopcionDetailView,
    SolicitudAdopcionDecisionView,
    AdopcionListView,
    ContadoresFamiliaView,
)

urlpatterns = [
    path('solicitudes/', SolicitudAdopcionListCreateView.as_view(), name='solicitudes-list'),
    path('solicitudes/mis-contadores/', ContadoresFamiliaView.as_view(), name='solicitudes-contadores'),
    path('solicitudes/<int:pk>/', SolicitudAdopcionDetailView.as_view(), name='solicitudes-detail'),
    path('solicitudes/<int:pk>/<str:accion>/', SolicitudAdopcionDecisionView.as_view(), name='solicitudes-decision'),
    path('adopciones/', AdopcionListView.as_view(), name='adopciones-list'),
]
