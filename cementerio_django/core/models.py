from django.db import models
from django.contrib.auth.models import User

# Modelo para el Perfil del Usuario
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombreC = models.CharField(max_length=40, null=False, blank=False, default="Desconocido")
    email = models.EmailField(null=False, blank=False, default="Desconocido")
    telefono = models.IntegerField(null=False, blank=False, default=9999999999)
    direccion = models.CharField(max_length=50, null=False, blank=False, default="Desconocido")
    ciudad = models.CharField(max_length=40, null=False, blank=False, default="Desconocido")

    def __str__(self) -> str:
        return f'Perfil de {self.user.username}'

# Modelo para las Bovedas
class Boveda(models.Model):
    numero = models.AutoField(primary_key=True, null=False, blank=False,)
    ubicacion = models.CharField(max_length=100, null=False, blank=False,)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Bóveda {self.numero}"

    class Meta:
        verbose_name_plural = "Bóvedas disponibles"


# Modelo para alquilar Bovedas
class Alquiler(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    boveda = models.ForeignKey(Boveda, on_delete=models.CASCADE)
    fecha_alquiler = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bóveda {self.boveda.numero}'  

    class Meta:
        verbose_name_plural = 'Alquileres'

# Modelo para crear difuntos
class Difunto(models.Model):
    documento = models.IntegerField(primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    fecha_defuncion = models.DateField()
    fecha_ingreso_boveda = models.DateField()
    boveda_asignada = models.ForeignKey(Alquiler, on_delete=models.CASCADE, verbose_name='asignar boveda')
    familiar = models.ForeignKey(User, on_delete=models.CASCADE)