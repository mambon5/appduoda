from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro_profe_view, name='registro_profe'),
    path('login/', auth_views.LoginView.as_view(template_name='gestio/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_profe_view, name='dashboard_profe'),
    path('pagament-pares/', views.pagament_pares_view, name='pagament_pares'),
    path('registro-alumne/', views.registro_alumne_view, name='registro_alumne'),
    path('verificar-email/', views.verify_email_view, name='verify_email'),
]
