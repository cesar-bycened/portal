from django.db import models
from django.conf import settings
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
import re


class Convocatoria(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    programas_educativos = models.ManyToManyField(
        "control_escolar.ProgramaEducativo",
        through="ConvocatoriaPrograma",
        related_name="convocatorias"
    )

    activo = models.BooleanField(default=True)
    resultados_publicados = models.BooleanField(default=False)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

############
class ConvocatoriaPrograma(models.Model):

    convocatoria = models.ForeignKey(
        Convocatoria,
        on_delete=models.CASCADE,
        related_name="programas_convocatoria"
    )

    programa_educativo = models.ForeignKey(
        "control_escolar.ProgramaEducativo",
        on_delete=models.CASCADE,
        related_name="convocatorias_programa"
    )

    fecha_entrevista = models.DateField(null=True, blank=True)
    hora_entrevista = models.TimeField(null=True, blank=True)
    lugar_entrevista = models.CharField(max_length=255, blank=True, null=True)

    indicaciones_entrevista = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales: qué llevar, modalidad, etc."
    )

    entrevista_publicada = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["convocatoria", "programa_educativo"],
                name="unique_programa_por_convocatoria"
            )
        ]

    def __str__(self):
        return f"{self.convocatoria} - {self.programa_educativo}"
    



########### 
class SolicitudAdmision(models.Model):

    class Estados(models.TextChoices):
        POSTULADO = "POSTULADO", "Postulado"
        EN_REVISION = "EN_REVISION", "En revisión"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes_admision"
    )

    convocatoria = models.ForeignKey(
        "aspirantes.Convocatoria",
        on_delete=models.PROTECT,
        related_name="solicitudes",
        editable=False
    )

    convocatoria_programa = models.ForeignKey(
        "aspirantes.ConvocatoriaPrograma",
        on_delete=models.PROTECT,
        related_name="solicitudes"
    )

    folio = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.POSTULADO
    )

    expediente_completo = models.BooleanField(
        default=False
    )

    fue_aceptado = models.BooleanField(
        default=False
    )

    fecha_postulacion = models.DateTimeField(
        auto_now_add=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Solicitud de Admisión"
        verbose_name_plural = "Solicitudes de Admisión"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "convocatoria"],
                name="unique_usuario_por_convocatoria"
            )
        ]

    def clean(self):
        if self.convocatoria_programa_id and self.convocatoria_id:
            if self.convocatoria_programa.convocatoria_id != self.convocatoria_id:
                raise ValidationError(
                    "El programa seleccionado no pertenece a la convocatoria indicada."
                )

    def generar_folio(self):
        clave_programa = self.convocatoria_programa.programa_educativo.clave.upper()

        folios_existentes = SolicitudAdmision.objects.filter(
            folio__startswith=clave_programa
        ).values_list("folio", flat=True)

        ultimo_numero = 0

        for folio in folios_existentes:
            coincidencia = re.match(
                rf"^{re.escape(clave_programa)}(\d+)$",
                folio
            )

            if coincidencia:
                numero = int(coincidencia.group(1))
                if numero > ultimo_numero:
                    ultimo_numero = numero

        siguiente_numero = ultimo_numero + 1

        return f"{clave_programa}{siguiente_numero:03d}"

    def save(self, *args, **kwargs):
        with transaction.atomic():

            if self.convocatoria_programa_id:
                self.convocatoria = self.convocatoria_programa.convocatoria

            self.clean()

            if not self.folio:
                self.folio = self.generar_folio()

            super().save(*args, **kwargs)

    @property
    def programa_educativo(self):
        return self.convocatoria_programa.programa_educativo

    def __str__(self):
        return self.folio
    


##########
class DocumentoExpediente(models.Model):

    class TiposDocumento(models.TextChoices):
        FICHA_PREINSCRIPCION = "FICHA_PREINSCRIPCION", "Ficha de preinscripción"
        ACTA_NACIMIENTO = "ACTA_NACIMIENTO", "Acta de nacimiento"
        CURP = "CURP", "CURP"
        IDENTIFICACION = "IDENTIFICACION", "Identificación oficial vigente"
        FICHA_PAGO = "FICHA_PAGO", "Ficha de pago"

    class Estados(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        CORRECCION = "CORRECCION", "Corrección requerida"

    solicitud = models.ForeignKey(
        "aspirantes.SolicitudAdmision",
        on_delete=models.CASCADE,
        related_name="documentos"
    )

    tipo_documento = models.CharField(
        max_length=50,
        choices=TiposDocumento.choices
    )

    archivo = models.FileField(
        upload_to="expedientes/"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.PENDIENTE
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Documento de Expediente"
        verbose_name_plural = "Documentos de Expediente"
        constraints = [
            models.UniqueConstraint(
                fields=["solicitud", "tipo_documento"],
                name="unique_documento_por_solicitud"
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.solicitud.folio}"
