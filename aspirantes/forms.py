from django import forms
from django.forms import inlineformset_factory
from .models import Convocatoria, ConvocatoriaPrograma
from control_escolar.models import ProgramaEducativo
from django import forms
from .models import Convocatoria, ConvocatoriaPrograma
from control_escolar.models import ProgramaEducativo
from django import forms
from django.db import transaction
from .models import Convocatoria, ConvocatoriaPrograma
from control_escolar.models import ProgramaEducativo
from django.forms import inlineformset_factory
from django import forms
from .models import DocumentoExpediente


class ConvocatoriaForm(forms.ModelForm):
    programas = forms.ModelMultipleChoiceField(
        label="Programas educativos ofertados",
        queryset=ProgramaEducativo.objects.filter(activo=True).order_by("nombre"),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            "required": "Selecciona al menos un programa educativo."
        }
    )

    class Meta:
        model = Convocatoria
        fields = [
            "nombre",
            "fecha_inicio",
            "fecha_fin",
            "activo",
            "resultados_publicados",
            "programas",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: Convocatoria de Admisión 2026",
                "autofocus": True,
            }),

            "fecha_inicio": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "fecha_fin": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "resultados_publicados": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "nombre": "Nombre de la convocatoria",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de cierre",
            "activo": "Convocatoria activa",
            "resultados_publicados": "Resultados publicados",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["programas"].queryset = ProgramaEducativo.objects.filter(
            activo=True
        ).order_by("nombre")

        if self.instance and self.instance.pk:
            self.fields["programas"].initial = self.instance.programas_convocatoria.filter(
                activo=True
            ).values_list(
                "programa_educativo_id",
                flat=True
            )

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error(
                "fecha_fin",
                "La fecha de cierre no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        convocatoria = super().save(commit=commit)

        if commit:
            self.guardar_programas(convocatoria)

        return convocatoria

    def guardar_programas(self, convocatoria):
        programas_seleccionados = self.cleaned_data.get("programas")

        if not programas_seleccionados:
            return

        programas_ids = programas_seleccionados.values_list("id", flat=True)

        ConvocatoriaPrograma.objects.filter(
            convocatoria=convocatoria
        ).exclude(
            programa_educativo_id__in=programas_ids
        ).update(
            activo=False
        )

        for programa in programas_seleccionados:
            convocatoria_programa, created = ConvocatoriaPrograma.objects.get_or_create(
                convocatoria=convocatoria,
                programa_educativo=programa,
                defaults={
                    "activo": True,
                }
            )

            if not created and not convocatoria_programa.activo:
                convocatoria_programa.activo = True
                convocatoria_programa.save(update_fields=["activo"])


class ConvocatoriaProgramaForm(forms.ModelForm):
    class Meta:
        model = ConvocatoriaPrograma

        fields = [
            "fecha_entrevista",
            "hora_entrevista",
            "lugar_entrevista",
            "indicaciones_entrevista",
            "entrevista_publicada",
            "activo",
        ]

        widgets = {
            "fecha_entrevista": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "hora_entrevista": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time",
            }),
            "lugar_entrevista": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: Aula 3, Auditorio, Dirección, etc.",
            }),
            "indicaciones_entrevista": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Indicaciones para el aspirante",
            }),
            "entrevista_publicada": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "fecha_entrevista": "Fecha de entrevista",
            "hora_entrevista": "Hora de entrevista",
            "lugar_entrevista": "Lugar de entrevista",
            "indicaciones_entrevista": "Indicaciones de entrevista",
            "entrevista_publicada": "Publicar entrevista",
            "activo": "Programa activo en convocatoria",
        }


ConvocatoriaProgramaFormSet = inlineformset_factory(
    Convocatoria,
    ConvocatoriaPrograma,
    form=ConvocatoriaProgramaForm,
    extra=0,
    can_delete=False,
)   



class DocumentoExpedienteUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentoExpediente
        fields = [
            "archivo",
        ]

        widgets = {
            "archivo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "application/pdf",
            }),
        }

        labels = {
            "archivo": "Archivo PDF",
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")

        if not archivo:
            return archivo

        if not archivo.name.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Solo se permiten archivos PDF."
            )

        limite = 5 * 1024 * 1024

        if archivo.size > limite:
            raise forms.ValidationError(
                "El archivo no debe superar los 5 MB."
            )

        return archivo
    


class DocumentoRevisionForm(forms.ModelForm):
    class Meta:
        model = DocumentoExpediente
        fields = [
            "estado",
            "observaciones",
        ]

        widgets = {
            "estado": forms.Select(attrs={
                "class": "form-select form-select-sm",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control form-control-sm",
                "rows": 2,
                "placeholder": "Observaciones para el aspirante",
            }),
        }

        labels = {
            "estado": "Estado",
            "observaciones": "Observaciones",
        }

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        observaciones = cleaned_data.get("observaciones")

        if estado == DocumentoExpediente.Estados.CORRECCION and not observaciones:
            self.add_error(
                "observaciones",
                "Agrega una observación cuando solicites corrección."
            )

        return cleaned_data    
