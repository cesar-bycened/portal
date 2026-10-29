from rest_framework import viewsets
from .serializers import *
from .models import *
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
#API
from .models import ProgramaEducativo
from .forms import ProgramaEducativoForm
from usuarios.permissions import EsSuperAdministrador


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = ProgramaEducativo.objects.all()
    serializer_class = ProgramaSerializer
    permission_classes = [EsSuperAdministrador]



class ProgramaEducativoListView(ListView): #LoginRequiredMixin, 
    model = ProgramaEducativo
    template_name = "programas.html"
    context_object_name = "programas"
    paginate_by = 10

    def get_queryset(self):
        queryset = ProgramaEducativo.objects.all().order_by("nombre")

        q = self.request.GET.get("q")

        if q:
            queryset = queryset.filter(nombre__icontains=q) | queryset.filter(clave__icontains=q)

        return queryset
    

class ProgramaEducativoCreateView(CreateView):  #LoginRequiredMixin, SuccessMessageMixin, 
    model = ProgramaEducativo
    form_class = ProgramaEducativoForm
    template_name = "crearPrograma.html"
    success_url = reverse_lazy("programas")
    success_message = "Programa educativo creado correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Nuevo programa educativo"
        context["boton"] = "Guardar programa"
        return context    
    

class ProgramaEducativoDeleteView(SuccessMessageMixin, DeleteView): #LoginRequiredMixin, 
    model = ProgramaEducativo
    template_name = "confirm_delete.html"
    context_object_name = "programa"
    success_url = reverse_lazy("programas")
    success_message = "Programa educativo eliminado correctamente."


class ProgramaEducativoUpdateView(SuccessMessageMixin, UpdateView):     # LoginRequiredMixin, 
    model = ProgramaEducativo
    form_class = ProgramaEducativoForm
    template_name = "editar.html"
    success_url = reverse_lazy("programas")
    success_message = "Programa educativo actualizado correctamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar programa educativo"
        context["boton"] = "Actualizar programa"
        return context    
    

class ProgramaEducativoDetailView(DetailView):  #LoginRequiredMixin, 
    model = ProgramaEducativo
    template_name = "detalle.html"
    context_object_name = "programa"
