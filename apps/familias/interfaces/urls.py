from django.urls import path
from apps.familias.interfaces.views import MiFamiliaView, CondicionesHogarView, FamiliaAdminListView

urlpatterns = [
    path('familias/', FamiliaAdminListView.as_view(), name='familias-admin-list'),
    path('familias/mia/', MiFamiliaView.as_view(), name='mi-familia'),
    path('familias/mia/condiciones-hogar/', CondicionesHogarView.as_view(), name='condiciones-hogar'),
]
