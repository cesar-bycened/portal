from django import forms
from .models import Perfil
from django.contrib.auth.forms import AuthenticationForm


class PerfilAspiranteForm(forms.ModelForm):
    class Meta:
        model = Perfil

        fields = [
            # Datos personales
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "nacionalidad",
            "sexo",
            "estado_civil",
            "curp",
            "rfc",
            "estado_nacimiento",

            # Contacto y domicilio
            "telefono_principal",
            "telefono_alterno",
            "pais_residencia",
            "codigo_postal",
            "localidad_colonia",
            "domicilio_calle",
            "numero_domicilio",

            # Información familiar
            "tiene_hijos",
            "dependientes_economicos",

            # Antecedentes académicos
            "nivel_escolaridad",
            "institucion_procedencia",
            "estado_institucion",
            "municipio_institucion",
            "cuenta_con_titulo",
            "cuenta_con_cedula",

            # Información laboral
            "trabaja_actualmente",
            "lugar_trabajo",
            "puesto_cargo",
            "antiguedad_laboral",
            "descripcion_actividades",

            # Inclusión y diversidad
            "pueblo_originario",
            "cual_pueblo",
            "tiene_discapacidad",
            "tiene_diagnostico",

            # Archivo
            "fotografia",
        ]

        labels = {
            "nombres": "Nombre(s)",
            "apellido_paterno": "Apellido paterno",
            "apellido_materno": "Apellido materno",
            "fecha_nacimiento": "Fecha de nacimiento",
            "nacionalidad": "Nacionalidad",
            "sexo": "Sexo",
            "estado_civil": "Estado civil",
            "curp": "CURP",
            "rfc": "RFC",
            "estado_nacimiento": "Estado de nacimiento",

            "telefono_principal": "Teléfono principal",
            "telefono_alterno": "Teléfono alterno",
            "pais_residencia": "País de residencia",
            "codigo_postal": "Código postal",
            "localidad_colonia": "Localidad / Colonia",
            "domicilio_calle": "Calle",
            "numero_domicilio": "Número de domicilio",

            "tiene_hijos": "¿Tiene hijos?",
            "dependientes_economicos": "¿Tiene dependientes económicos?",

            "nivel_escolaridad": "Nivel de escolaridad",
            "institucion_procedencia": "Institución de procedencia",
            "estado_institucion": "Estado de la institución",
            "municipio_institucion": "Municipio de la institución",
            "cuenta_con_titulo": "¿Cuenta con título?",
            "cuenta_con_cedula": "¿Cuenta con cédula?",

            "trabaja_actualmente": "¿Trabaja actualmente?",
            "lugar_trabajo": "Lugar de trabajo",
            "puesto_cargo": "Puesto o cargo",
            "antiguedad_laboral": "Antigüedad laboral",
            "descripcion_actividades": "Descripción de actividades",

            "pueblo_originario": "¿Pertenece a un pueblo originario?",
            "cual_pueblo": "¿Cuál pueblo originario?",
            "tiene_discapacidad": "¿Tiene alguna discapacidad?",
            "tiene_diagnostico": "¿Cuenta con diagnóstico?",
            "fotografia": "Fotografía",
        }

        widgets = {
            # Datos personales
            "nombres": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre(s)",
                "autofocus": True,
            }),

            "apellido_paterno": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Apellido paterno",
            }),

            "apellido_materno": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Apellido materno",
            }),

            "fecha_nacimiento": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "nacionalidad": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: Mexicana",
            }),

            "sexo": forms.Select(attrs={
                "class": "form-select",
            }),

            "estado_civil": forms.Select(attrs={
                "class": "form-select",
            }),

            "curp": forms.TextInput(attrs={
                "class": "form-control text-uppercase",
                "placeholder": "CURP",
                "maxlength": "18",
            }),

            "rfc": forms.TextInput(attrs={
                "class": "form-control text-uppercase",
                "placeholder": "RFC",
                "maxlength": "13",
            }),

            "estado_nacimiento": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Estado de nacimiento",
            }),

            # Contacto y domicilio
            "telefono_principal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono principal",
            }),

            "telefono_alterno": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono alterno",
            }),

            "pais_residencia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "País de residencia",
            }),

            "codigo_postal": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Código postal",
                "maxlength": "10",
            }),

            "localidad_colonia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Localidad o colonia",
            }),

            "domicilio_calle": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Calle",
            }),

            "numero_domicilio": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de domicilio",
            }),

            # Información familiar
            "tiene_hijos": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "dependientes_economicos": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            # Antecedentes académicos
            "nivel_escolaridad": forms.Select(attrs={
                "class": "form-select",
            }),

            "institucion_procedencia": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Institución de procedencia",
            }),

            "estado_institucion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Estado donde se ubica la institución",
            }),

            "municipio_institucion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Municipio donde se ubica la institución",
            }),

            "cuenta_con_titulo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "cuenta_con_cedula": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            # Información laboral
            "trabaja_actualmente": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "lugar_trabajo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lugar de trabajo",
            }),

            "puesto_cargo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Puesto o cargo",
            }),

            "antiguedad_laboral": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: 2 años, 6 meses",
            }),

            "descripcion_actividades": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe brevemente tus actividades laborales",
            }),

            # Inclusión y diversidad
            "pueblo_originario": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "cual_pueblo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Indica el pueblo originario",
            }),

            "tiene_discapacidad": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "tiene_diagnostico": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            # Archivo
            "fotografia": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
        }

        help_texts = {
            "curp": "Ingresa tu CURP a 18 caracteres.",
            "rfc": "Campo opcional. Debe tener 12 o 13 caracteres.",
            "fotografia": "Formato recomendado: JPG o PNG.",
            "cual_pueblo": "Solo llenar si pertenece a un pueblo originario.",
            "lugar_trabajo": "Solo llenar si trabaja actualmente.",
            "puesto_cargo": "Solo llenar si trabaja actualmente.",
            "antiguedad_laboral": "Solo llenar si trabaja actualmente.",
            "descripcion_actividades": "Solo llenar si trabaja actualmente.",
        }

    def clean_curp(self):
        curp = self.cleaned_data.get("curp")

        if curp:
            curp = curp.strip().upper()

            if len(curp) != 18:
                raise forms.ValidationError(
                    "La CURP debe tener 18 caracteres."
                )

        return curp

    def clean_rfc(self):
        rfc = self.cleaned_data.get("rfc")

        if rfc:
            rfc = rfc.strip().upper()

            if len(rfc) not in [12, 13]:
                raise forms.ValidationError(
                    "El RFC debe tener 12 o 13 caracteres."
                )

        return rfc

    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres")

        if nombres:
            nombres = nombres.strip().title()

        return nombres

    def clean_apellido_paterno(self):
        apellido = self.cleaned_data.get("apellido_paterno")

        if apellido:
            apellido = apellido.strip().title()

        return apellido

    def clean_apellido_materno(self):
        apellido = self.cleaned_data.get("apellido_materno")

        if apellido:
            apellido = apellido.strip().title()

        return apellido

    def clean_telefono_principal(self):
        telefono = self.cleaned_data.get("telefono_principal")

        if telefono:
            telefono = telefono.strip()

        return telefono

    def clean_telefono_alterno(self):
        telefono = self.cleaned_data.get("telefono_alterno")

        if telefono:
            telefono = telefono.strip()

        return telefono

    def clean(self):
        cleaned_data = super().clean()

        trabaja_actualmente = cleaned_data.get("trabaja_actualmente")
        lugar_trabajo = cleaned_data.get("lugar_trabajo")
        puesto_cargo = cleaned_data.get("puesto_cargo")

        pueblo_originario = cleaned_data.get("pueblo_originario")
        cual_pueblo = cleaned_data.get("cual_pueblo")

        if trabaja_actualmente:
            if not lugar_trabajo:
                self.add_error(
                    "lugar_trabajo",
                    "Indica el lugar de trabajo."
                )

            if not puesto_cargo:
                self.add_error(
                    "puesto_cargo",
                    "Indica el puesto o cargo."
                )

        if pueblo_originario and not cual_pueblo:
            self.add_error(
                "cual_pueblo",
                "Indica a qué pueblo originario pertenece."
            )

        return cleaned_data
    


class LoginComunidadForm(AuthenticationForm):
    username = forms.CharField(
        label="Número de control",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Número de control",
            "autofocus": True,
        })
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Contraseña",
        })
    )    