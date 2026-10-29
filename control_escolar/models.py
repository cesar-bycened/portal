from django.db import models

# Create your models here.
class ProgramaEducativo(models.Model):

    class Niveles(models.TextChoices):
        BACHILLERATO = "BACHILLERATO", "Bachillerato"
        LICENCIATURA = "LICENCIATURA", "Licenciatura"
        ESPECIALIDAD = "ESPECIALIDAD", "Especialidad"
        MAESTRIA = "MAESTRIA", "Maestría"
        DOCTORADO = "DOCTORADO", "Doctorado"

    clave = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=255
    )

    nivel = models.CharField(
        max_length=20,
        choices=Niveles.choices,
        default=Niveles.LICENCIATURA
    )

    duracion_semestres = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Programa Educativo"
        verbose_name_plural = "Programas Educativos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.clave} - {self.nombre}"
    


  