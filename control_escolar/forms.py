from django import forms
from .models import ProgramaEducativo


class ProgramaEducativoForm(forms.ModelForm):
    class Meta:
        model = ProgramaEducativo
        fields = [
            "clave",
            "nombre",
            "nivel",
            "duracion_semestres",
            "descripcion",
            "activo",
        ]

        widgets = {
            "clave": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: LEAM, LEP, BACH",
                "autofocus": True,
            }),

            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del programa educativo",
            }),

            "nivel": forms.Select(attrs={
                "class": "form-select",
            }),

            "duracion_semestres": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: 8",
                "min": 1,
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descripción breve del programa educativo",
            }),

            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "clave": "Clave del programa",
            "nombre": "Nombre del programa educativo",
            "nivel": "Nivel educativo",
            "duracion_semestres": "Duración en semestres",
            "descripcion": "Descripción",
            "activo": "Programa activo",
        }

        help_texts = {
            "clave": "Clave corta del programa. Ejemplo: LEAM, LEP, BACH.",
            "activo": "Desactiva este campo si el programa ya no debe aparecer en convocatorias.",
        }

    def clean_clave(self):
        clave = self.cleaned_data.get("clave")

        if clave:
            clave = clave.strip().upper()

        return clave

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        if nombre:
            nombre = nombre.strip()

        return nombre

    def clean_duracion_semestres(self):
        duracion = self.cleaned_data.get("duracion_semestres")

        if duracion is not None and duracion <= 0:
            raise forms.ValidationError(
                "La duración debe ser mayor a 0."
            )

        return duracion