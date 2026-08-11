from django.contrib.gis.db import models

class Parcela(models.Model):

    municipio_codigo = models.CharField(
        max_length=5,
        db_index=True,
        null=True,
        blank=True,
    )

    local_id = models.CharField(max_length=50)

    referencia_catastral = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    etiqueta = models.CharField(
        max_length=50,
        blank=True,
    )

    area = models.IntegerField(
        null=True,
        blank=True,
    )

    fecha_alta = models.CharField(
        max_length=50,
        blank=True,
    )

    geom = models.GeometryField(
        srid=25830,
    )