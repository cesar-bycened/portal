from rest_framework import routers
from django.urls import path, include
from control_escolar import views

router = routers.DefaultRouter()

router.register(r'programa', views.ProgramaViewSet)

urlpatterns = [
    path('api_programas/', include(router.urls)),
    path('programas/', views.ProgramaEducativoListView.as_view(), name='programas'),
    path('crearPrograma/', views.ProgramaEducativoCreateView.as_view(), name='createPrograma'),
    path('programas/<int:pk>/eliminar/', views.ProgramaEducativoDeleteView.as_view(), name="programas_delete"),
    path('programas/<int:pk>/editar/', views.ProgramaEducativoUpdateView.as_view(), name="programas_update"),
    path('programas/<int:pk>/', views.ProgramaEducativoDetailView.as_view(), name="programas_detail"),
]