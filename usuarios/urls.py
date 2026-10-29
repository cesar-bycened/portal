from rest_framework import routers
from django.urls import path, include
from usuarios import views

router = routers.DefaultRouter()

router.register(r'usuario', views.UsuarioViewSet)
router.register(r'perfil', views.PerfilViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path("perfil/aspirante/",   views.PerfilAspiranteUpdateView.as_view(),  name="perfil_aspirante"),
    path("login/aspirante/",    views.LoginAspiranteView.as_view(),         name="login_asp"),
    path("login/comunidad/",    views.LoginComunidadView.as_view(),         name="login_comunidad"),
    path("redirigir/",          views.PostLoginRedirectView.as_view(),      name="post_login_redirect"), 
    path("perfil/",             views.PerfilUsuarioDetailView.as_view(),    name="perfil_usuario"), 
    path("cerrar-sesion/",      views.CerrarSesionView.as_view(),           name="cerrar_sesion"),
]
