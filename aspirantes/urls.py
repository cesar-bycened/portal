from rest_framework import routers
from django.urls import path, include
from aspirantes import views
from django.conf import settings
from django.conf.urls.static import static


router = routers.SimpleRouter()

router.register(r'convocatoria', views.ConvocatoriaViewSet)

urlpatterns = [
    path('api_convocatorias/', include(router.urls)),
    path("dashboard/", views.AspiranteDashboardView.as_view(), name="aspirante_dashboard"),
        path(
        "convocatorias/",
        views.ConvocatoriaListView.as_view(),
        name="convocatorias_list"
    ),

    path(
        "convocatorias/nueva/",
        views.ConvocatoriaCreateView.as_view(),
        name="convocatorias_create"
    ),

    path(
        "convocatorias/<int:pk>/",
        views.ConvocatoriaDetailView.as_view(),
        name="convocatorias_detail"
    ),

    path(
        "convocatorias/<int:pk>/editar/",
        views.ConvocatoriaUpdateView.as_view(),
        name="convocatorias_update"
    ),

    path(
        "convocatorias/<int:pk>/eliminar/",
        views.ConvocatoriaDeleteView.as_view(),
        name="convocatorias_delete"
    ),
    path("convocatorias/<int:pk>/entrevistas/", views.ConvocatoriaEntrevistasUpdateView.as_view(), name="convocatorias_entrevistas"),
    path(
        "aspirante/convocatorias/",
        views.ConvocatoriaAspiranteListView.as_view(),
        name="aspirante_convocatorias_list"
    ),

    path(
        "aspirante/convocatorias/<int:pk>/",
        views.ConvocatoriaAspiranteDetailView.as_view(),
        name="aspirante_convocatorias_detail"
    ),

    path(
        "aspirante/postular/<int:pk>/",
        views.PostularProgramaView.as_view(),
        name="aspirante_postular_programa"
    ),

    path(
        "aspirante/solicitudes/<int:pk>/",
        views.SolicitudAspiranteDetailView.as_view(),
        name="solicitud_aspirante_detail"
    ),

    path(
        "aspirante/solicitudes/<int:solicitud_pk>/documentos/<str:tipo_documento>/subir/",
        views.DocumentoExpedienteUploadView.as_view(),
        name="documento_expediente_upload"
    ),
    path(
        "admin/solicitudes/",
        views.AdminSolicitudAdmisionListView.as_view(),
        name="admin_solicitudes_list"
    ),

    path(
        "admin/solicitudes/<int:pk>/",
        views.AdminSolicitudAdmisionDetailView.as_view(),
        name="admin_solicitud_detail"
    ),

#     path(
#     "aspirante/solicitudes/<int:pk>/expediente/",
#     views.ExpedienteAspiranteDetailView.as_view(),
#     name="expediente_aspirante_detail"
# ),

    path(
        "admin/documentos/<int:pk>/revisar/",
        views.AdminDocumentoRevisionView.as_view(),
        name="admin_documento_revision"
    ),
    path(
        "convocatorias/<int:pk>/resultados/",
        views.AdminConvocatoriaResultadosView.as_view(),
        name="admin_convocatoria_resultados"
    ),
    path(
    "convocatorias/<int:pk>/aceptados/",
    views.AdminAceptadosConvocatoriaView.as_view(),
    name="admin_aceptados_convocatoria"
    ),

    path(
        "aspirante/solicitudes/<int:pk>/expediente/",
        views.ExpedienteAspiranteDetailView.as_view(),
        name="expediente_aspirante_detail"
    ),

    path(
        "aspirante/solicitudes/<int:solicitud_pk>/documentos/<str:tipo_documento>/subir/",
        views.DocumentoExpedienteUploadView.as_view(),
        name="documento_expediente_upload"
    ),
    path(
        "admin/aspirantes/estadisticas/",
        views.AdminAspirantesEstadisticasView.as_view(),
        name="admin_aspirantes_estadisticas"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
