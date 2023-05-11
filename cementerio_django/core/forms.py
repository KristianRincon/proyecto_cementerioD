from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Alquiler, Profile, Boveda, Difunto

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    nombreC = forms.CharField(label='Nombre Completo', required=True)
    telefono = forms.IntegerField(label='Telefono', required=True)
    direccion = forms.CharField(label='Direccion', required=True)
    ciudad = forms.CharField(label='Ciudad', required=True)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirma Contraseña', widget=forms.PasswordInput, required=True)


    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'nombreC', 'email', 'telefono', 'direccion', 'ciudad' ]
        help_texts = {k:"" for k in fields}

# Con esta función se guardan los datos ingresados por el usuario 
# ademas se crea automaticamente un perfil para el usuario sin necesidad del archivo signals.py
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            user_profile = Profile.objects.create(
                user=user,
                nombreC=self.cleaned_data.get('nombreC'),
                email=self.cleaned_data.get('email'),
                telefono=self.cleaned_data.get('telefono'),
                direccion=self.cleaned_data.get('direccion'),
                ciudad=self.cleaned_data.get('ciudad'),
            )
            user_profile.save()
        return user
    

class BovedaForm(forms.ModelForm):
    class Meta:
        model = Boveda
        fields = ['ubicacion', 'disponible']
        labels = {
            'ubicacion': 'Ubicación',
            'disponible': 'Disponible'
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nombreC', 'email', 'telefono', 'direccion', 'ciudad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombreC'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['ciudad'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user = user_profile.user
        user.email = self.cleaned_data.get('email')
        user.save()
        user_profile.save()
        return user_profile
    


# Formulario para create difunto
class DifuntoFormCreate(forms.ModelForm):
    def __init__(self, usuario, *args, **kwargs):
        bovedas_asignadas = kwargs.pop('bovedas_asignadas', None)
        super().__init__(*args, **kwargs)
        # Filtrar las opciones de la llave foránea 'boveda_asignada'
        qs = Alquiler.objects.filter(usuario=usuario)
        if bovedas_asignadas:
            qs = qs.exclude(id__in=bovedas_asignadas)
        self.fields['boveda_asignada'].queryset = qs

    class Meta:
        model = Difunto
        fields = ['documento', 'nombre_completo', 'fecha_nacimiento', 'fecha_defuncion', 'fecha_ingreso_boveda', 'boveda_asignada']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'fecha_defuncion': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'fecha_ingreso_boveda': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'boveda_asignada': forms.Select(),
        }
    


# # Formulario para detalle difunto

class DifuntoForm(forms.ModelForm):
    boveda_actual = forms.CharField(label='Bóveda asignada actualmente', disabled=True, required=False)

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar las opciones de la llave foránea 'boveda_asignada'
        queryset = Alquiler.objects.filter(usuario=usuario, difunto__isnull=True)
        # Agregar la boveda asignada actualmente a las opciones del campo 'boveda_asignada'
        if self.instance and self.instance.boveda_asignada:
            queryset |= Alquiler.objects.filter(pk=self.instance.boveda_asignada.pk)
        self.fields['boveda_asignada'].queryset = queryset
        self.fields['documento'].disabled = True

    class Meta:
        model = Difunto
        fields = ['documento', 'nombre_completo', 'fecha_nacimiento', 'fecha_defuncion', 'fecha_ingreso_boveda', 'boveda_asignada', 'boveda_actual']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'fecha_defuncion': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'fecha_ingreso_boveda': forms.DateInput(attrs={'type': 'date', 'format': '%d de %B de %Y'}),
            'boveda_asignada': forms.Select(),
        }

        # Indicar que el campo 'boveda_actual' no es requerido
        required = {
            'boveda_actual': False
        }

        # Esto eliminará el campo boveda_actual del diccionario cleaned_data que se usa para validar el formulario. 
        # De esta manera, el campo no se considerará obligatorio y no impedirá que se actualice el difunto.
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.pop('boveda_actual', None)
        return cleaned_data



class EliminarDifuntoForm(forms.Form):
    OPCIONES_CONFIRMAR = (
        ('si', 'Si'),
        ('no', 'No')
    )
    confirmacion = forms.ChoiceField(
        required=True,
        label='¿Está seguro de que desea eliminar este difunto?',
        widget=forms.RadioSelect(choices=OPCIONES_CONFIRMAR)
    )
