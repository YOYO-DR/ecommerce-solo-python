from django.db import models

# Create your models here.
class AuditDates(models.Model):
    """ Modelo para auditar fechas de creación y actualización de registros """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']