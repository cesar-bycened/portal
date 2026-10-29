from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.models import Perfil
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Convocatoria
from .forms import ConvocatoriaForm, ConvocatoriaProgramaFormSet
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Convocatoria, ConvocatoriaPrograma
from .mixins import *
from django.utils import timezone
from .forms import DocumentoExpedienteUploadForm
from django.db.models import Q
from .forms import *
from django.db.models import Count
from urllib.parse import urlencode
from django.urls import reverse
from usuarios.permissions import EsSuperAdministrador

# Create your views here.
class ConvocatoriaViewSet(viewsets.ModelViewSet):
    queryset = Convocatoria.objects.all()
    serializer_class = ConvocatoriaSerializer
    permission_classes = [EsSuperAdministrador]



class AspiranteDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashbooard.html"

    campos_requeridos_perfil = [
        ("nombres", "Nombre(s)"),
        ("apellido_paterno", "Apellido paterno"),
        ("fecha_nacimiento", "Fecha de nacimiento"),
        ("sexo", "Sexo"),
        ("estado_civil", "Estado civil"),
        ("curp", "CURP"),
        ("telefono_principal", "Teléfono principal"),
        ("codigo_postal", "Código postal"),
        ("localidad_colonia", "Localidad / Colonia"),
        ("domicilio_calle", "Calle"),
        ("numero_domicilio", "Número de domicilio"),
        ("nivel_escolaridad", "Nivel de escolaridad"),
        ("institucion_procedencia", "Institución de procedencia"),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        perfil, created = Perfil.objects.get_or_create(
            usuario=self.request.user
        )

        campos_pendientes = []

        for campo, etiqueta in self.campos_requeridos_perfil:
            valor = getattr(perfil, campo, None)

            if valor is None or valor == "":
                campos_pendientes.append(etiqueta)

        total_campos = len(self.campos_requeridos_perfil)
        campos_completados = total_campos - len(campos_pendientes)

        porcentaje_perfil = round((campos_completados / total_campos) * 100) if total_campos else 0
        perfil_completo = len(campos_pendientes) == 0

        hoy = timezone.localdate()

        convocatorias_activas = Convocatoria.objects.filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        ).order_by("-fecha_inicio")

        solicitud_actual = SolicitudAdmision.objects.filter(
            usuario=self.request.user
        ).select_related(
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).order_by(
            "-fecha_postulacion"
        ).first()

        documentos_cargados = 0
        total_documentos = len(DocumentoExpediente.TiposDocumento.choices)
        porcentaje_expediente = 0

        if solicitud_actual:
            documentos_cargados = solicitud_actual.documentos.count()

            if total_documentos > 0:
                porcentaje_expediente = round(
                    (documentos_cargados / total_documentos) * 100
                )

        context["perfil"] = perfil
        context["perfil_creado"] = created
        context["campos_pendientes"] = campos_pendientes
        context["total_campos"] = total_campos
        context["campos_completados"] = campos_completados
        context["porcentaje_perfil"] = porcentaje_perfil
        context["perfil_completo"] = perfil_completo

        context["convocatorias_activas"] = convocatorias_activas
        context["total_convocatorias_activas"] = convocatorias_activas.count()

        context["solicitud_actual"] = solicitud_actual
        context["documentos_cargados"] = documentos_cargados
        context["total_documentos"] = total_documentos
        context["porcentaje_expediente"] = porcentaje_expediente

        return context
    



class AdminConvocatoriaRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user

        return (
            user.is_staff
            or user.rol == "ADMINISTRATIVO"
            or user.rol == "SUPERADMIN"
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            "No tienes permisos para acceder a este apartado."
        )

        if self.request.user.is_authenticated:
            return redirect("aspirante_dashboard")

        return redirect("login_aspirante")


class ConvocatoriaListView(AdminConvocatoriaRequiredMixin, ListView):
    model = Convocatoria
    template_name = "list.html"
    context_object_name = "convocatorias"
    paginate_by = 10

    def get_queryset(self):
        queryset = Convocatoria.objects.all().order_by("-fecha_inicio")

        q = self.request.GET.get("q")
        estado = self.request.GET.get("estado")

        if q:
            queryset = queryset.filter(nombre__icontains=q)

        if estado == "activas":
            queryset = queryset.filter(activo=True)

        if estado == "inactivas":
            queryset = queryset.filter(activo=False)

        return queryset


class ConvocatoriaDetailView(AdminConvocatoriaRequiredMixin, DetailView):
    model = Convocatoria
    template_name = "detail.html"
    context_object_name = "convocatoria"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        programas = self.object.programas_convocatoria.filter(
            activo=True
        ).select_related(
            "programa_educativo"
        ).annotate(
            total_aspirantes=Count("solicitudes")
        ).order_by(
            "programa_educativo__nombre"
        )

        total_aspirantes = self.object.solicitudes.count()

        context["programas"] = programas
        context["total_aspirantes"] = total_aspirantes

        return context


class ConvocatoriaCreateView(AdminConvocatoriaRequiredMixin, CreateView):
    model = Convocatoria
    form_class = ConvocatoriaForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Nueva convocatoria"
        context["boton"] = "Guardar convocatoria"
        return context

    def form_valid(self, form):
        self.object = form.save()

        messages.success(
            self.request,
            "Convocatoria creada correctamente."
        )

        return redirect("convocatorias_detail", pk=self.object.pk)


class ConvocatoriaUpdateView(AdminConvocatoriaRequiredMixin, UpdateView):
    model = Convocatoria
    form_class = ConvocatoriaForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Editar convocatoria"
        context["boton"] = "Actualizar convocatoria"
        return context

    def form_valid(self, form):
        self.object = form.save()

        messages.success(
            self.request,
            "Convocatoria actualizada correctamente."
        )

        return redirect("convocatorias_detail", pk=self.object.pk)
    

class ConvocatoriaEntrevistasUpdateView(AdminConvocatoriaRequiredMixin, View):
    template_name = "entrevistas_form.html"

    def get(self, request, pk):
        convocatoria = get_object_or_404(Convocatoria, pk=pk)

        queryset = ConvocatoriaPrograma.objects.filter(
            convocatoria=convocatoria,
            activo=True
        ).select_related(
            "programa_educativo"
        ).order_by(
            "programa_educativo__nombre"
        )

        formset = ConvocatoriaProgramaFormSet(
            instance=convocatoria,
            queryset=queryset
        )

        return render(request, self.template_name, {
            "convocatoria": convocatoria,
            "formset": formset,
            "titulo": "Configurar entrevistas",
        })

    def post(self, request, pk):
        convocatoria = get_object_or_404(Convocatoria, pk=pk)

        queryset = ConvocatoriaPrograma.objects.filter(
            convocatoria=convocatoria,
            activo=True
        ).select_related(
            "programa_educativo"
        ).order_by(
            "programa_educativo__nombre"
        )

        formset = ConvocatoriaProgramaFormSet(
            request.POST,
            instance=convocatoria,
            queryset=queryset
        )

        if formset.is_valid():
            formset.save()

            messages.success(
                request,
                "Entrevistas configuradas correctamente."
            )

            return redirect("convocatorias_detail", pk=convocatoria.pk)

        return render(request, self.template_name, {
            "convocatoria": convocatoria,
            "formset": formset,
            "titulo": "Configurar entrevistas",
        })


class ConvocatoriaDeleteView(AdminConvocatoriaRequiredMixin, DeleteView):
    model = Convocatoria
    success_url = reverse_lazy("convocatorias_list")

    def get(self, request, *args, **kwargs):
        return redirect("convocatorias_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Convocatoria eliminada correctamente."
        )
        return super().form_valid(form)    
    

########## CONVOCATORIAS ASPIRANTE #########
class ConvocatoriaAspiranteListView(AspiranteRequiredMixin, ListView):
    model = Convocatoria
    template_name = "aspirante/convocatorias_list.html"
    context_object_name = "convocatorias"

    def get_queryset(self):
        hoy = timezone.localdate()

        return Convocatoria.objects.filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        ).order_by("-fecha_inicio")


class ConvocatoriaAspiranteDetailView(AspiranteRequiredMixin, DetailView):
    model = Convocatoria
    template_name = "aspirante/convocatoria_detail.html"
    context_object_name = "convocatoria"

    def get_queryset(self):
        hoy = timezone.localdate()

        return Convocatoria.objects.filter(
            activo=True,
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        convocatoria = self.object

        context["programas"] = convocatoria.programas_convocatoria.filter(
            activo=True
        ).select_related(
            "programa_educativo"
        ).order_by(
            "programa_educativo__nombre"
        )

        context["solicitud_existente"] = SolicitudAdmision.objects.filter(
            usuario=self.request.user,
            convocatoria=convocatoria
        ).first()

        return context   


class PostularProgramaView(AspiranteRequiredMixin, View):
    def post(self, request, pk):
        convocatoria_programa = get_object_or_404(
            ConvocatoriaPrograma.objects.select_related(
                "convocatoria",
                "programa_educativo"
            ),
            pk=pk,
            activo=True,
            convocatoria__activo=True,
        )

        perfil = getattr(request.user, "perfil", None)

        if not perfil or not perfil.perfil_completo:
            messages.warning(
                request,
                "Primero debes completar tu perfil antes de postularte."
            )

            return redirect("perfil_aspirante")

        solicitud_existente = SolicitudAdmision.objects.filter(
            usuario=request.user,
            convocatoria=convocatoria_programa.convocatoria
        ).first()

        if solicitud_existente:
            messages.info(
                request,
                "Ya tienes una solicitud registrada para esta convocatoria."
            )

            return redirect("solicitud_aspirante_detail", pk=solicitud_existente.pk)

        solicitud = SolicitudAdmision.objects.create(
            usuario=request.user,
            convocatoria_programa=convocatoria_programa,
        )

        messages.success(
            request,
            f"Postulación registrada correctamente. Tu folio es {solicitud.folio}."
        )

        return redirect("solicitud_aspirante_detail", pk=solicitud.pk)
    

class SolicitudAspiranteDetailView(AspiranteRequiredMixin, DetailView):
    model = SolicitudAdmision
    template_name = "aspirante/solicitud_detail.html"
    context_object_name = "solicitud"

    def get_queryset(self):
        return SolicitudAdmision.objects.filter(
            usuario=self.request.user
        ).select_related(
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).prefetch_related(
            "documentos"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solicitud = self.object

        documentos_subidos = solicitud.documentos.all()

        documentos_por_tipo = {
            documento.tipo_documento: documento
            for documento in documentos_subidos
        }

        tipos_documentos = []

        for valor, etiqueta in DocumentoExpediente.TiposDocumento.choices:
            documento = documentos_por_tipo.get(valor)

            tipos_documentos.append({
                "valor": valor,
                "etiqueta": etiqueta,
                "documento": documento,
            })

        total_documentos = len(DocumentoExpediente.TiposDocumento.choices)
        documentos_cargados = documentos_subidos.count()

        documentos_aprobados = documentos_subidos.filter(
            estado=DocumentoExpediente.Estados.APROBADO
        ).count()

        context["tipos_documentos"] = tipos_documentos
        context["total_documentos"] = total_documentos
        context["documentos_cargados"] = documentos_cargados
        context["documentos_aprobados"] = documentos_aprobados

        context["porcentaje_expediente"] = round(
            (documentos_cargados / total_documentos) * 100
        ) if total_documentos else 0

        context["porcentaje_aprobado"] = round(
            (documentos_aprobados / total_documentos) * 100
        ) if total_documentos else 0

        return context
    

# class DocumentoExpedienteUploadView(AspiranteRequiredMixin, View):
    def post(self, request, solicitud_pk, tipo_documento):
        solicitud = get_object_or_404(
            SolicitudAdmision,
            pk=solicitud_pk,
            usuario=request.user
        )

        tipos_validos = [
            valor for valor, etiqueta in DocumentoExpediente.TiposDocumento.choices
        ]

        if tipo_documento not in tipos_validos:
            messages.error(
                request,
                "Tipo de documento no válido."
            )

            return redirect("solicitud_aspirante_detail", pk=solicitud.pk)

        form = DocumentoExpedienteUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            archivo = form.cleaned_data["archivo"]

            documento, created = DocumentoExpediente.objects.update_or_create(
                solicitud=solicitud,
                tipo_documento=tipo_documento,
                defaults={
                    "archivo": archivo,
                    "estado": DocumentoExpediente.Estados.PENDIENTE,
                    "observaciones": None,
                    "fecha_revision": None,
                }
            )

            messages.success(
                request,
                "Documento cargado correctamente."
            )
        else:
            messages.error(
                request,
                "No se pudo cargar el documento. Verifica que sea PDF y no supere los 5 MB."
            )

        return redirect("solicitud_aspirante_detail", pk=solicitud.pk)    
    

# ADMIN SOLICITUD ADMISION
class AdminSolicitudAdmisionListView(AdminConvocatoriaRequiredMixin, ListView):
    model = SolicitudAdmision
    template_name = "admin_solicitudes_list.html"
    context_object_name = "solicitudes"
    paginate_by = 20

    def get_queryset(self):
        queryset = SolicitudAdmision.objects.select_related(
            "usuario",
            "usuario__perfil",
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).prefetch_related(
            "documentos"
        ).order_by(
            "-fecha_postulacion"
        )

        convocatoria_id = self.request.GET.get("convocatoria")
        programa_id = self.request.GET.get("programa")
        q = self.request.GET.get("q")

        if convocatoria_id:
            queryset = queryset.filter(
                convocatoria_id=convocatoria_id
            )

        if programa_id:
            queryset = queryset.filter(
                convocatoria_programa_id=programa_id
            )

        if q:
            queryset = queryset.filter(
                Q(folio__icontains=q)
                | Q(usuario__email__icontains=q)
                | Q(usuario__perfil__nombres__icontains=q)
                | Q(usuario__perfil__apellido_paterno__icontains=q)
                | Q(usuario__perfil__apellido_materno__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        convocatoria_id = self.request.GET.get("convocatoria")

        context["convocatorias"] = Convocatoria.objects.all().order_by(
            "-fecha_inicio"
        )

        programas_queryset = ConvocatoriaPrograma.objects.filter(
            activo=True
        ).select_related(
            "programa_educativo",
            "convocatoria",
        ).order_by(
            "programa_educativo__nombre"
        )

        if convocatoria_id:
            programas_queryset = programas_queryset.filter(
                convocatoria_id=convocatoria_id
            )

        context["programas"] = programas_queryset

        return context
    


class AdminSolicitudAdmisionDetailView(AdminConvocatoriaRequiredMixin, DetailView):
    model = SolicitudAdmision
    template_name = "admin_solicitud_detail.html"
    context_object_name = "solicitud"

    def get_queryset(self):
        return SolicitudAdmision.objects.select_related(
            "usuario",
            "usuario__perfil",
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).prefetch_related(
            "documentos"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solicitud = self.object

        documentos_subidos = solicitud.documentos.all()

        documentos_por_tipo = {
            documento.tipo_documento: documento
            for documento in documentos_subidos
        }

        tipos_documentos = []

        for valor, etiqueta in DocumentoExpediente.TiposDocumento.choices:
            documento = documentos_por_tipo.get(valor)

            tipos_documentos.append({
                "valor": valor,
                "etiqueta": etiqueta,
                "documento": documento,
                "revision_form": DocumentoRevisionForm(instance=documento) if documento else None,
            })

        total_documentos = len(DocumentoExpediente.TiposDocumento.choices)
        documentos_cargados = documentos_subidos.count()
        documentos_aprobados = documentos_subidos.filter(
            estado=DocumentoExpediente.Estados.APROBADO
        ).count()

        porcentaje_cargado = round(
            (documentos_cargados / total_documentos) * 100
        ) if total_documentos else 0

        porcentaje_aprobado = round(
            (documentos_aprobados / total_documentos) * 100
        ) if total_documentos else 0

        context["perfil_aspirante"] = getattr(
            solicitud.usuario,
            "perfil",
            None
        )

        context["tipos_documentos"] = tipos_documentos
        context["total_documentos"] = total_documentos
        context["documentos_cargados"] = documentos_cargados
        context["documentos_aprobados"] = documentos_aprobados
        context["porcentaje_cargado"] = porcentaje_cargado
        context["porcentaje_aprobado"] = porcentaje_aprobado

        return context
    


class AdminDocumentoRevisionView(AdminConvocatoriaRequiredMixin, View):
    def post(self, request, pk):
        documento = get_object_or_404(
            DocumentoExpediente.objects.select_related(
                "solicitud",
                "solicitud__convocatoria",
                "solicitud__convocatoria_programa",
                "solicitud__convocatoria_programa__programa_educativo",
            ),
            pk=pk
        )

        form = DocumentoRevisionForm(
            request.POST,
            instance=documento
        )

        if form.is_valid():
            documento = form.save(commit=False)
            documento.fecha_revision = timezone.now()
            documento.save()

            solicitud = documento.solicitud

            total_documentos = len(DocumentoExpediente.TiposDocumento.choices)

            documentos_aprobados = solicitud.documentos.filter(
                estado=DocumentoExpediente.Estados.APROBADO
            ).count()

            solicitud.expediente_completo = documentos_aprobados == total_documentos
            solicitud.save(update_fields=["expediente_completo", "actualizado_en"])

            messages.success(
                request,
                "Documento revisado correctamente."
            )
        else:
            messages.error(
                request,
                "No se pudo guardar la revisión del documento."
            )

        return redirect(
            "admin_solicitud_detail",
            pk=documento.solicitud.pk
        )
    


class AdminConvocatoriaResultadosView(AdminConvocatoriaRequiredMixin, View):
    template_name = "admin_resultados_convocatoria.html"

    def get(self, request, pk):
        convocatoria = get_object_or_404(
            Convocatoria,
            pk=pk
        )

        programa_id = request.GET.get("programa")
        q = request.GET.get("q")

        programas = ConvocatoriaPrograma.objects.filter(
            convocatoria=convocatoria,
            activo=True
        ).select_related(
            "programa_educativo"
        ).annotate(
            total_aspirantes=Count("solicitudes"),
            total_aceptados=Count(
                "solicitudes",
                filter=Q(solicitudes__fue_aceptado=True)
            )
        ).order_by(
            "programa_educativo__nombre"
        )

        solicitudes = SolicitudAdmision.objects.filter(
            convocatoria=convocatoria
        ).select_related(
            "usuario",
            "usuario__perfil",
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).order_by(
            "convocatoria_programa__programa_educativo__nombre",
            "folio"
        )

        if programa_id:
            solicitudes = solicitudes.filter(
                convocatoria_programa_id=programa_id
            )

        if q:
            solicitudes = solicitudes.filter(
                Q(folio__icontains=q)
                | Q(usuario__email__icontains=q)
                | Q(usuario__perfil__nombres__icontains=q)
                | Q(usuario__perfil__apellido_paterno__icontains=q)
                | Q(usuario__perfil__apellido_materno__icontains=q)
            )

        context = {
            "convocatoria": convocatoria,
            "programas": programas,
            "solicitudes": solicitudes,
            "programa_id": programa_id,
            "q": q,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        convocatoria = get_object_or_404(
            Convocatoria,
            pk=pk
        )

        accion = request.POST.get("accion")
        programa_id = request.POST.get("programa_id")

        if accion == "guardar_aceptados":
            aceptados_ids = request.POST.getlist("aceptados")

            solicitudes_base = SolicitudAdmision.objects.filter(
                convocatoria=convocatoria
            )

            if programa_id:
                solicitudes_base = solicitudes_base.filter(
                    convocatoria_programa_id=programa_id
                )

            solicitudes_base.update(
                fue_aceptado=False
            )

            solicitudes_base.filter(
                id__in=aceptados_ids
            ).update(
                fue_aceptado=True
            )

            messages.success(
                request,
                "Lista de aspirantes aceptados actualizada correctamente."
            )

        elif accion == "publicar_resultados":
            convocatoria.resultados_publicados = True
            convocatoria.save(update_fields=["resultados_publicados", "actualizado_en"])

            messages.success(
                request,
                "Resultados publicados correctamente."
            )

        elif accion == "ocultar_resultados":
            convocatoria.resultados_publicados = False
            convocatoria.save(update_fields=["resultados_publicados", "actualizado_en"])

            messages.warning(
                request,
                "Los resultados fueron ocultados para los aspirantes."
            )

        return redirect(
            "admin_convocatoria_resultados",
            pk=convocatoria.pk
        )
    


# ASEPTAR ASPIRANTES

class AdminAceptadosConvocatoriaView(AdminConvocatoriaRequiredMixin, View):
    template_name = "admin_aceptados_convocatoria.html"

    def get(self, request, pk):
        convocatoria = get_object_or_404(
            Convocatoria,
            pk=pk
        )

        programa_id = request.GET.get("programa")
        q = request.GET.get("q")

        programas = ConvocatoriaPrograma.objects.filter(
            convocatoria=convocatoria,
            activo=True
        ).select_related(
            "programa_educativo"
        ).annotate(
            total_aspirantes=Count("solicitudes"),
            total_aceptados=Count(
                "solicitudes",
                filter=Q(solicitudes__fue_aceptado=True)
            )
        ).order_by(
            "programa_educativo__nombre"
        )

        solicitudes = SolicitudAdmision.objects.filter(
            convocatoria=convocatoria
        ).select_related(
            "usuario",
            "usuario__perfil",
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).order_by(
            "convocatoria_programa__programa_educativo__nombre",
            "folio"
        )

        if programa_id:
            solicitudes = solicitudes.filter(
                convocatoria_programa_id=programa_id
            )

        if q:
            solicitudes = solicitudes.filter(
                Q(folio__icontains=q)
                | Q(usuario__email__icontains=q)
                | Q(usuario__perfil__nombres__icontains=q)
                | Q(usuario__perfil__apellido_paterno__icontains=q)
                | Q(usuario__perfil__apellido_materno__icontains=q)
            )

        total_solicitudes = SolicitudAdmision.objects.filter(
            convocatoria=convocatoria
        ).count()

        total_aceptados = SolicitudAdmision.objects.filter(
            convocatoria=convocatoria,
            fue_aceptado=True
        ).count()

        context = {
            "convocatoria": convocatoria,
            "programas": programas,
            "solicitudes": solicitudes,
            "programa_id": programa_id,
            "q": q,
            "total_solicitudes": total_solicitudes,
            "total_aceptados": total_aceptados,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        convocatoria = get_object_or_404(
            Convocatoria,
            pk=pk
        )

        accion = request.POST.get("accion")
        programa_id = request.POST.get("programa_id")
        q = request.POST.get("q")

        if accion == "guardar_aceptados":
            solicitudes_en_pantalla = request.POST.getlist("solicitudes_en_pantalla")
            aceptados_ids = request.POST.getlist("aceptados")

            solicitudes_base = SolicitudAdmision.objects.filter(
                convocatoria=convocatoria,
                id__in=solicitudes_en_pantalla
            )

            solicitudes_base.update(
                fue_aceptado=False
            )

            solicitudes_base.filter(
                id__in=aceptados_ids
            ).update(
                fue_aceptado=True
            )

            messages.success(
                request,
                "Lista de aspirantes aceptados actualizada correctamente."
            )

        elif accion == "publicar_resultados":
            convocatoria.resultados_publicados = True
            convocatoria.save(
                update_fields=[
                    "resultados_publicados",
                    "actualizado_en",
                ]
            )

            messages.success(
                request,
                "Resultados publicados correctamente."
            )

        elif accion == "ocultar_resultados":
            convocatoria.resultados_publicados = False
            convocatoria.save(
                update_fields=[
                    "resultados_publicados",
                    "actualizado_en",
                ]
            )

            messages.warning(
                request,
                "Los resultados fueron ocultados para los aspirantes."
            )

        url = reverse(
            "admin_aceptados_convocatoria",
            kwargs={
                "pk": convocatoria.pk
            }
        )

        params = {}

        if programa_id:
            params["programa"] = programa_id

        if q:
            params["q"] = q

        if params:
            url = f"{url}?{urlencode(params)}"

        return redirect(url)
    

class ExpedienteAspiranteDetailView(AspiranteRequiredMixin, DetailView):
    model = SolicitudAdmision
    template_name = "aspirante/expediente_detail.html"
    context_object_name = "solicitud"

    def get_queryset(self):
        return SolicitudAdmision.objects.filter(
            usuario=self.request.user
        ).select_related(
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).prefetch_related(
            "documentos"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solicitud = self.object
        documentos_subidos = solicitud.documentos.all()

        documentos_por_tipo = {
            documento.tipo_documento: documento
            for documento in documentos_subidos
        }

        tipos_documentos = []

        for valor, etiqueta in DocumentoExpediente.TiposDocumento.choices:
            tipos_documentos.append({
                "valor": valor,
                "etiqueta": etiqueta,
                "documento": documentos_por_tipo.get(valor),
            })

        total_documentos = len(DocumentoExpediente.TiposDocumento.choices)
        documentos_cargados = documentos_subidos.count()

        documentos_aprobados = documentos_subidos.filter(
            estado=DocumentoExpediente.Estados.APROBADO
        ).count()

        context["tipos_documentos"] = tipos_documentos
        context["total_documentos"] = total_documentos
        context["documentos_cargados"] = documentos_cargados
        context["documentos_aprobados"] = documentos_aprobados

        context["porcentaje_expediente"] = round(
            (documentos_cargados / total_documentos) * 100
        ) if total_documentos else 0

        context["porcentaje_aprobado"] = round(
            (documentos_aprobados / total_documentos) * 100
        ) if total_documentos else 0

        return context


class DocumentoExpedienteUploadView(AspiranteRequiredMixin, View):
    def post(self, request, solicitud_pk, tipo_documento):
        solicitud = get_object_or_404(
            SolicitudAdmision,
            pk=solicitud_pk,
            usuario=request.user
        )

        tipos_validos = [
            valor for valor, etiqueta in DocumentoExpediente.TiposDocumento.choices
        ]

        if tipo_documento not in tipos_validos:
            messages.error(
                request,
                "Tipo de documento no válido."
            )

            return redirect("expediente_aspirante_detail", pk=solicitud.pk)

        documento_actual = DocumentoExpediente.objects.filter(
            solicitud=solicitud,
            tipo_documento=tipo_documento
        ).first()

        if documento_actual and documento_actual.estado == DocumentoExpediente.Estados.APROBADO:
            messages.warning(
                request,
                "Este documento ya fue aprobado y no puede ser reemplazado."
            )

            return redirect("expediente_aspirante_detail", pk=solicitud.pk)

        form = DocumentoExpedienteUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            archivo = form.cleaned_data["archivo"]

            DocumentoExpediente.objects.update_or_create(
                solicitud=solicitud,
                tipo_documento=tipo_documento,
                defaults={
                    "archivo": archivo,
                    "estado": DocumentoExpediente.Estados.PENDIENTE,
                    "observaciones": None,
                    "fecha_revision": None,
                }
            )

            messages.success(
                request,
                "Documento cargado correctamente."
            )
        else:
            messages.error(
                request,
                "No se pudo cargar el documento. Verifica que sea PDF y no supere los 5 MB."
            )

        return redirect("expediente_aspirante_detail", pk=solicitud.pk)        


from datetime import date

class AdminAspirantesEstadisticasView(AdminConvocatoriaRequiredMixin, TemplateView):
    template_name = "aspirantes_estadisticas.html"

    def calcular_edad(self, fecha_nacimiento):
        if not fecha_nacimiento:
            return None

        hoy = date.today()

        return (
            hoy.year
            - fecha_nacimiento.year
            - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        )

    def obtener_rango_edad(self, edad):
        if edad is None:
            return "Sin dato"

        if edad < 18:
            return "Menor de 18"

        if edad <= 20:
            return "18 a 20"

        if edad <= 25:
            return "21 a 25"

        if edad <= 30:
            return "26 a 30"

        if edad <= 40:
            return "31 a 40"

        return "Más de 40"

    def agrupar_perfiles(self, perfiles, campo):
        datos = {}

        for perfil in perfiles:
            valor = getattr(perfil, campo, None)

            if valor is None or valor == "":
                valor = "Sin dato"

            datos[valor] = datos.get(valor, 0) + 1

        return [
            {
                "nombre": nombre,
                "total": total,
            }
            for nombre, total in sorted(
                datos.items(),
                key=lambda item: item[1],
                reverse=True
            )
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        convocatoria_id = self.request.GET.get("convocatoria")
        programa_id = self.request.GET.get("programa")

        solicitudes = SolicitudAdmision.objects.select_related(
            "usuario",
            "usuario__perfil",
            "convocatoria",
            "convocatoria_programa",
            "convocatoria_programa__programa_educativo",
        ).prefetch_related(
            "documentos"
        )

        if convocatoria_id:
            solicitudes = solicitudes.filter(convocatoria_id=convocatoria_id)

        if programa_id:
            solicitudes = solicitudes.filter(convocatoria_programa_id=programa_id)

        total_solicitudes = solicitudes.count()

        user_ids = solicitudes.values_list("usuario_id", flat=True).distinct()

        perfiles = Perfil.objects.filter(
            usuario_id__in=user_ids
        )

        total_perfiles = perfiles.count()

        # =========================
        # ESTADÍSTICAS GENERALES
        # =========================
        total_aceptados = solicitudes.filter(
            fue_aceptado=True
        ).count()

        total_no_seleccionados = solicitudes.filter(
            fue_aceptado=False,
            convocatoria__resultados_publicados=True
        ).count()

        total_expedientes_completos = solicitudes.filter(
            expediente_completo=True
        ).count()

        total_expedientes_incompletos = total_solicitudes - total_expedientes_completos

        # =========================
        # DOCUMENTOS
        # =========================
        solicitud_ids = solicitudes.values_list("id", flat=True)

        documentos = DocumentoExpediente.objects.filter(
            solicitud_id__in=solicitud_ids
        )

        total_documentos_cargados = documentos.count()

        total_documentos_aprobados = documentos.filter(
            estado=DocumentoExpediente.Estados.APROBADO
        ).count()

        total_documentos_correccion = documentos.filter(
            estado=DocumentoExpediente.Estados.CORRECCION
        ).count()

        total_documentos_requeridos = len(DocumentoExpediente.TiposDocumento.choices)

        total_documentos_posibles = total_solicitudes * total_documentos_requeridos

        porcentaje_carga_documentos = round(
            (total_documentos_cargados / total_documentos_posibles) * 100
        ) if total_documentos_posibles else 0

        porcentaje_documentos_aprobados = round(
            (total_documentos_aprobados / total_documentos_posibles) * 100
        ) if total_documentos_posibles else 0

        # =========================
        # POR PROGRAMA
        # =========================
        aspirantes_por_programa = solicitudes.values(
            "convocatoria_programa__programa_educativo__nombre"
        ).annotate(
            total=Count("id")
        ).order_by("-total")

        # =========================
        # POR CONVOCATORIA
        # =========================
        aspirantes_por_convocatoria = solicitudes.values(
            "convocatoria__nombre"
        ).annotate(
            total=Count("id")
        ).order_by("-total")

        # =========================
        # PERFIL DEL ASPIRANTE
        # =========================
        aspirantes_por_sexo = self.agrupar_perfiles(perfiles, "sexo")
        aspirantes_por_estado_civil = self.agrupar_perfiles(perfiles, "estado_civil")
        aspirantes_por_nacionalidad = self.agrupar_perfiles(perfiles, "nacionalidad")
        aspirantes_por_estado_nacimiento = self.agrupar_perfiles(perfiles, "estado_nacimiento")
        aspirantes_por_escolaridad = self.agrupar_perfiles(perfiles, "nivel_escolaridad")
        aspirantes_por_institucion = self.agrupar_perfiles(perfiles, "institucion_procedencia")

        # =========================
        # RANGOS DE EDAD
        # =========================
        rangos_edad = {}

        for perfil in perfiles:
            edad = self.calcular_edad(perfil.fecha_nacimiento)
            rango = self.obtener_rango_edad(edad)
            rangos_edad[rango] = rangos_edad.get(rango, 0) + 1

        aspirantes_por_edad = [
            {
                "nombre": nombre,
                "total": total,
            }
            for nombre, total in rangos_edad.items()
        ]

        # =========================
        # DATOS SOCIODEMOGRÁFICOS
        # =========================
        total_trabajan = perfiles.filter(
            trabaja_actualmente=True
        ).count()

        total_con_hijos = perfiles.filter(
            tiene_hijos=True
        ).count()

        total_con_dependientes = perfiles.filter(
            dependientes_economicos=True
        ).count()

        total_pueblo_originario = perfiles.filter(
            pueblo_originario=True
        ).count()

        total_discapacidad = perfiles.filter(
            tiene_discapacidad=True
        ).count()

        total_diagnostico = perfiles.filter(
            tiene_diagnostico=True
        ).count()

        convocatorias = Convocatoria.objects.all().order_by("-fecha_inicio")

        programas = ConvocatoriaPrograma.objects.select_related(
            "programa_educativo",
            "convocatoria"
        ).filter(
            activo=True
        ).order_by(
            "programa_educativo__nombre"
        )

        if convocatoria_id:
            programas = programas.filter(convocatoria_id=convocatoria_id)

        context.update({
            "convocatoria_id": convocatoria_id,
            "programa_id": programa_id,
            "convocatorias": convocatorias,
            "programas": programas,

            "total_solicitudes": total_solicitudes,
            "total_perfiles": total_perfiles,
            "total_aceptados": total_aceptados,
            "total_no_seleccionados": total_no_seleccionados,
            "total_expedientes_completos": total_expedientes_completos,
            "total_expedientes_incompletos": total_expedientes_incompletos,

            "total_documentos_cargados": total_documentos_cargados,
            "total_documentos_aprobados": total_documentos_aprobados,
            "total_documentos_correccion": total_documentos_correccion,
            "total_documentos_requeridos": total_documentos_requeridos,
            "total_documentos_posibles": total_documentos_posibles,
            "porcentaje_carga_documentos": porcentaje_carga_documentos,
            "porcentaje_documentos_aprobados": porcentaje_documentos_aprobados,

            "aspirantes_por_programa": aspirantes_por_programa,
            "aspirantes_por_convocatoria": aspirantes_por_convocatoria,
            "aspirantes_por_sexo": aspirantes_por_sexo,
            "aspirantes_por_estado_civil": aspirantes_por_estado_civil,
            "aspirantes_por_nacionalidad": aspirantes_por_nacionalidad,
            "aspirantes_por_estado_nacimiento": aspirantes_por_estado_nacimiento,
            "aspirantes_por_escolaridad": aspirantes_por_escolaridad,
            "aspirantes_por_institucion": aspirantes_por_institucion,
            "aspirantes_por_edad": aspirantes_por_edad,

            "total_trabajan": total_trabajan,
            "total_con_hijos": total_con_hijos,
            "total_con_dependientes": total_con_dependientes,
            "total_pueblo_originario": total_pueblo_originario,
            "total_discapacidad": total_discapacidad,
            "total_diagnostico": total_diagnostico,
        })

        return context
    
