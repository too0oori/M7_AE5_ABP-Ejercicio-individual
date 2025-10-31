from django.db import models

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=50, db_index=True) #se añade index
    precio = models.IntegerField()
    disponible = models.BooleanField(default=True)