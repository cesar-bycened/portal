from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text="Número de control institucional para personal interno."
    )

    class Roles(models.TextChoices):
        ASPIRANTE = "ASPIRANTE", "Aspirante"
        ALUMNO = "ALUMNO", "Alumno"
        DOCENTE = "DOCENTE", "Docente"
        ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo"
        SUPERADMIN = "SUPERADMIN", "Super Administrador"

    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.ASPIRANTE
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Correo personal del usuario."
    )

    email_institucional = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Correo institucional asignado por la institución."
    )

    google_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Identificador único proporcionado por Google OAuth."
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    def es_aspirante(self):
        return self.rol == self.Roles.ASPIRANTE


    def es_admin_aspirantes(self):
        return (
            self.is_superuser
            or self.rol == self.Roles.SUPERADMIN
            or self.groups.filter(name="ADMIN_ASPIRANTES").exists()
        )


    def es_admin_control_escolar(self):
        return (
            self.is_superuser
            or self.rol == self.Roles.SUPERADMIN
            or self.groups.filter(name="ADMIN_CONTROL_ESCOLAR").exists()
        )

    def __str__(self):
        return (
            self.username
            or self.email_institucional
            or self.email
            or f"Usuario {self.id}"
        )
    



class Perfil(models.Model):

    SEXO_CHOICES = (
        ('M', 'Mujer'),
        ('H', 'Hombre'),
        ('O', 'Otro / Prefiero no mencionar'),
    )

    ESTADO_CIVIL_CHOICES = (
        ('SOLTERO', 'Soltero/a'),
        ('CASADO', 'Casado/a'),
        ('DIVORCIADO', 'Divorciado/a'),
        ('VIUDO', 'Viudo/a'),
        ('UNION_LIBRE', 'Unión Libre'),
    )

    ESCOLARIDAD_CHOICES = (
        ('SECUNDARIA', 'Secundaria'),
        ('PREPARATORIA', 'Preparatoria / Bachillerato'),
        ('LICENCIATURA', 'Licenciatura'),
        ('MAESTRIA', 'Maestría'),
        ('DOCTORADO', 'Doctorado'),
    )

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    # ==========================
    # DATOS PERSONALES
    # ==========================

    nombres = models.CharField(max_length=100)

    apellido_paterno = models.CharField(max_length=100)

    apellido_materno = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    nacionalidad = models.CharField(
        max_length=50,
        default='Mexicana'
    )

    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        null=True,
        blank=True
    )

    estado_civil = models.CharField(
        max_length=15,
        choices=ESTADO_CIVIL_CHOICES,
        null=True,
        blank=True
    )

    curp = models.CharField(
        max_length=18,
        unique=True,
        null=True,
        blank=True
    )

    rfc = models.CharField(
        max_length=13,
        blank=True,
        null=True
    )

    estado_nacimiento = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    # ==========================
    # CONTACTO Y DOMICILIO
    # ==========================

    telefono_principal = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    telefono_alterno = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    pais_residencia = models.CharField(
        max_length=50,
        default='México'
    )

    codigo_postal = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    localidad_colonia = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    domicilio_calle = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    numero_domicilio = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    # ==========================
    # INFORMACIÓN FAMILIAR
    # ==========================

    tiene_hijos = models.BooleanField(
        default=False
    )

    dependientes_economicos = models.BooleanField(
        default=False
    )

    # ==========================
    # ANTECEDENTES ACADÉMICOS
    # ==========================

    nivel_escolaridad = models.CharField(
        max_length=20,
        choices=ESCOLARIDAD_CHOICES,
        null=True,
        blank=True
    )

    institucion_procedencia = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    estado_institucion = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    municipio_institucion = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    cuenta_con_titulo = models.BooleanField(
        default=False
    )

    cuenta_con_cedula = models.BooleanField(
        default=False
    )

    # ==========================
    # INFORMACIÓN LABORAL
    # ==========================

    trabaja_actualmente = models.BooleanField(
        default=False
    )

    lugar_trabajo = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    puesto_cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    antiguedad_laboral = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    descripcion_actividades = models.TextField(
        blank=True,
        null=True
    )

    # ==========================
    # INCLUSIÓN Y DIVERSIDAD
    # ==========================

    pueblo_originario = models.BooleanField(
        default=False
    )

    cual_pueblo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    tiene_discapacidad = models.BooleanField(
        default=False
    )

    tiene_diagnostico = models.BooleanField(
        default=False
    )

    # ==========================
    # ARCHIVOS
    # ==========================

    fotografia = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True
    )

    # ==========================
    # AUDITORÍA
    # ==========================

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    @property
    def perfil_completo(self):
        campos_requeridos = [
            self.nombres,
            self.apellido_paterno,
            self.fecha_nacimiento,
            self.sexo,
            self.estado_civil,
            self.curp,
            self.telefono_principal,
            self.codigo_postal,
            self.localidad_colonia,
            self.domicilio_calle,
            self.numero_domicilio,
            self.nivel_escolaridad,
            self.institucion_procedencia,
        ]

        return all(campos_requeridos)

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno or ''}".strip()

    def __str__(self):
        return self.nombre_completo
