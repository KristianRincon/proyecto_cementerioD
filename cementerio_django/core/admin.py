from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Boveda, Alquiler, Difunto
from django.contrib.auth.models import User


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfiles de Usuario'

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Alquiler)

@admin.register(Boveda)
class BovedaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'ubicacion', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('ubicacion',)


class DifuntoAdmin(admin.ModelAdmin):
    list_display = ('documento', 'nombre_completo', 'fecha_nacimiento', 'fecha_defuncion', 'fecha_ingreso_boveda', 'boveda_asignada', 'familiar')
    search_fields = ('documento', 'nombre_completo', 'familiar__username')
    list_filter = ('boveda_asignada',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.familiar = request.user
        obj.save()

admin.site.register(Difunto, DifuntoAdmin)
