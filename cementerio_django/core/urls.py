from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('boveda/', views.boveda, name='boveda'),
    path('lista_bovedas/', views.lista_bovedas, name='lista_bovedas'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('alquilar_boveda/', views.alquilar_boveda, name='alquilar_boveda'),
    path('mis_bovedas/', views.mis_bovedas, name='mis_bovedas'),
    path('difuntos/list/', views.lista_difuntos, name='difunto_list'),
    path('difuntos/create/', views.difunto_create, name='difunto_nuevo'),
    path('difuntos/<int:documento>/', views.difunto_detail, name='difunto_detail'),
    path('difuntos/eliminar_difunto/<int:pk>/', views.eliminar_difunto, name='eliminar_difunto'),
    path('devolver_boveda/<int:boveda_numero>/', views.devolver_boveda, name='devolver_boveda'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)