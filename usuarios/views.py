
from .models import *
from .forms import *
from .serializers import *
from django.views import View
from django.urls import reverse_lazy
from rest_framework import viewsets
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .permissions import EsSuperAdministrador


# API
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsSuperAdministrador]


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [EsSuperAdministrador]


# Index
def inicio(request):
    return render(request, "inicio.html")


# DETALLE USUARIO
class PerfilUsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Perfil
    template_name = "perfil.html"
    context_object_name = "perfil"

    def get_object(self, queryset=None):
        perfil, created = Perfil.objects.get_or_create(
            usuario=self.request.user
        )
        return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        perfil = self.object

        context["perfil_completo"] = perfil.perfil_completo if hasattr(perfil, "perfil_completo") else False

        return context



# REDIRECCION EN LOGIN
class PostLoginRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        storage = messages.get_messages(request)
        for _ in storage:
            pass

        user = request.user

        if user.rol == "ASPIRANTE":
            return redirect("aspirante_dashboard")

        if user.rol == "ALUMNO":
            # Más adelante puedes crear un dashboard propio para alumnos
            return redirect("aspirante_dashboard")

        if user.rol == "DOCENTE":
            # Más adelante puedes crear un dashboard propio para docentes
            return redirect("aspirante_dashboard")

        # SUPERADMIN / SUPERUSER
        # Se revisa antes porque tus métodos de permisos regresan True para superuser.
        if user.is_superuser or user.rol == "SUPERADMIN":
            return redirect("programas")

        # ADMINISTRATIVO
        if user.rol == "ADMINISTRATIVO":

            if user.es_admin_control_escolar():
                return redirect("programas")

            if user.es_admin_aspirantes():
                return redirect("convocatorias_list")

            messages.error(
                request,
                "Tu usuario administrativo no tiene un grupo de permisos asignado."
            )
            return redirect("login_comunidad")

        return redirect("login_aspirante")


# LOGIN ASPIRANTE   
class LoginAspiranteView(TemplateView):
    template_name = "login_asp.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("aspirante_dashboard")

        return super().dispatch(request, *args, **kwargs)
    

# SIGN OUT ASPIRANTE
class CerrarSesionView(LogoutView):
    next_page = reverse_lazy("inicio")
    

# ACTUALIZAR PERFIL ASPIRANTE
class PerfilAspiranteUpdateView(UpdateView):    #LoginRequiredMixin, SuccessMessageMixin, 
    model = Perfil
    form_class = PerfilAspiranteForm
    template_name = "perfil_aspirante_form.html"
    success_url = reverse_lazy("aspirante_dashboard")
    success_message = "Perfil actualizado correctamente."

    def get_object(self, queryset=None):
        perfil, created = Perfil.objects.get_or_create(
            usuario=self.request.user
        )
        return perfil 


# LOGIN COMUNIDAD V 1.0
class LoginComunidadView(LoginView):
    template_name = "login_comunidad.html"
    authentication_form = LoginComunidadForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("post_login_redirect")


