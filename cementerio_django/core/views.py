from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Difunto

# Create your views here.
def home(request):
    return render(request, 'home.html')

# Vista para registrar un usuario
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Usuario {username} creado')
            return redirect('home')
    else: # si se accede mediante el metodo GET
        form = UserRegisterForm()
        
    context = { 'form' : form }
    return render(request, 'register.html', context)

def profile(request):
    return render(request, 'profile.html')


# Vista para crear una boveda
@user_passes_test(lambda u: u.is_superuser)
def boveda(request):
    if request.method == 'POST':
        form = BovedaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_bovedas')
    else:
        form = BovedaForm()
    return render(request, 'boveda.html', {'form': form})

# Vista para ver las bovedas creadas solo para el administrador
def lista_bovedas(request):
    # Obtener todas las bóvedas disponibles
    bovedas = Boveda.objects.filter()
    #bovedas = Boveda.objects.filter(disponible=True)

    # Renderizar la plantilla lista_bovedas.html y pasarle el contexto
    context = {'bovedas': bovedas}
    return render(request, 'lista_bovedas.html', context)



# Vista para alquilar una Boveda
@login_required
def alquilar_boveda(request):
    bovedas_disponibles = Boveda.objects.filter(disponible=True)
    if request.method == 'POST':
        boveda_id = request.POST.get('boveda_id')
        try:
            boveda = Boveda.objects.get(pk=boveda_id)
            if boveda.disponible:
                alquiler = Alquiler(usuario=request.user, boveda=boveda)
                alquiler.save()
                boveda.disponible = False
                boveda.save()
                messages.success(request, f'Se ha alquilado la boveda {boveda.numero}')
                return redirect('alquilar_boveda')
            else:
                messages.error(request, 'La boveda seleccionada no está disponible')
        except ObjectDoesNotExist:
            messages.error(request, 'El id de la boveda seleccionada no es válido')
    return render(request, 'alquilar_boveda.html', {'bovedas_disponibles': bovedas_disponibles})



# Vista para ver las bovedas alquiladas
@login_required
def mis_bovedas(request):
    alquileres = Alquiler.objects.filter(usuario=request.user)
    bovedas_alquiladas = Alquiler.objects.filter(usuario=request.user, boveda__disponible=False)

    context = {'alquileres': alquileres, 'bovedas_alquiladas': bovedas_alquiladas}
    return render(request, 'mis_bovedas.html', context)
    #return render(request, 'mis_bovedas.html', {'alquileres': alquileres})


@login_required
def devolver_boveda(request, alquiler_id):
    alquiler = get_object_or_404(Alquiler, pk=alquiler_id, usuario=request.user)
    boveda = alquiler.boveda

    if boveda.difunto:
        messages.error(request, 'No puede devolver la boveda ya que tiene un difunto asignado.')
    else:
        boveda.disponible = True
        boveda.save()
        alquiler.delete()
        messages.success(request, 'La boveda ha sido devuelta exitosamente.')

    return redirect('mis_bovedas')



# Vista Para editar Perfil
@login_required
def edit_profile(request):
    # Buscamos el objeto Profile asociado al usuario actual
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if 'update' in request.POST:
            # Creamos el formulario con los datos enviados en el request y la instancia del objeto Profile
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado con éxito.')
                return redirect('edit_profile')
    else:
        # Creamos el formulario con la instancia del objeto Profile
        form = ProfileForm(instance=profile)

    # Pasamos el objeto Profile al contexto
    user_profile = profile
    context = {'form': form, 'user_profile': user_profile}
    return render(request, 'edit_profile.html', context)


# Vista para ver los difuntos
@login_required
def lista_difuntos(request):
    difuntos = Difunto.objects.filter(familiar=request.user)
    return render(request, 'difuntos/list.html', {'difuntos': difuntos})
    



# # Vista para crear un difunto   


def difunto_create(request):
    # Obtener el ID de la boveda que ya ha sido asignada a un difunto anteriormente
    bovedas_asignadas = Difunto.objects.filter(familiar=request.user).values_list('boveda_asignada', flat=True)
    if request.method == 'POST':
        # Pasar la lista de ID de bovedas asignadas a DifuntoForm
        form = DifuntoFormCreate(request.user, request.POST, bovedas_asignadas=bovedas_asignadas)
        if form.is_valid():
            difunto = form.save(commit=False)
            difunto.familiar = request.user
            difunto.save()
            messages.success(request, 'Difunto creado exitosamente.')
            return redirect('difunto_list')
    else:
        # Pasar la lista de ID de bovedas asignadas a DifuntoForm
        form = DifuntoFormCreate(request.user, bovedas_asignadas=bovedas_asignadas)
    context = {
        'form': form,
    }
    return render(request, 'difuntos/create.html', context)

    
# vista para editar difuntos


def difunto_detail(request, documento):
    difunto = get_object_or_404(Difunto, documento=documento, familiar=request.user)
    if request.method == 'POST':
        form = None
        if 'update' in request.POST:
            form = DifuntoForm(request.user, data=request.POST, instance=difunto)
            if form.is_valid():
                difunto_actualizado = form.save(commit=False)
                difunto_actualizado.save()
                messages.success(request, 'El difunto ha sido actualizado exitosamente.')
                return redirect('difunto_list')
        elif 'delete' in request.POST:
            # mostrar la ventana modal de confirmación
            return render(request, 'difuntos/eliminar_difunto.html', {'difunto': difunto})
    else:
        form = DifuntoForm(request.user, instance=difunto if difunto else None)
        # Obtener la boveda asignada actualmente y establecerla en el campo de solo lectura "boveda_actual"
    if difunto and difunto.boveda_asignada:
        form.fields['boveda_actual'].initial = difunto.boveda_asignada
    context = {
        'form': form,
        'difunto': difunto,
    }
    return render(request, 'difuntos/difunto_detail.html', context)





def eliminar_difunto(request, pk):
    difunto = get_object_or_404(Difunto, pk=pk, familiar=request.user)
    if request.method == 'POST' and request.POST.get('confirmacion') == 'True':
        difunto.delete()
        messages.success(request, 'El difunto ha sido eliminado exitosamente.')
        return redirect('difunto_list')
    return redirect('difunto_detail', pk=pk)