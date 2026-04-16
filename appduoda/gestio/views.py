from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Professor, Classe, Alumne, PagamentAlumne
from .forms import ProfessorRegistrationForm, ClasseForm, PagamentPareForm, AlumneRegistrationForm
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

def home(request):
    return render(request, 'gestio/home.html')

def registro_profe_view(request):
    if request.method == 'POST':
        form = ProfessorRegistrationForm(request.POST)
        if form.is_valid():
            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            # Create Professor profile
            professor = form.save(commit=False)
            professor.user = user
            professor.save()
            
            login(request, user)
            messages.success(request, "Registre completat amb èxit!")
            return redirect('dashboard_profe')
    else:
        form = ProfessorRegistrationForm()
    return render(request, 'gestio/registro_profe.html', {'form': form})

@login_required
def dashboard_profe_view(request):
    try:
        professor = request.user.professor_profile
    except Professor.DoesNotExist:
        messages.error(request, "L'usuari no té un perfil de professor vinculat.")
        return redirect('home')

    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            classe = form.save(commit=False)
            classe.professor = professor
            classe.save()
            messages.success(request, "Classe registrada correctament.")
            return redirect('dashboard_profe')
    else:
        form = ClasseForm()

    classes = Classe.objects.filter(professor=professor).order_by('-data')
    return render(request, 'gestio/dashboard_profe.html', {
        'form': form,
        'professor': professor,
        'classes': classes
    })

def pagament_pares_view(request):
    if request.method == 'POST':
        alumne_id = request.POST.get('alumne')
        hores = int(request.POST.get('hores', 1))
        concepte = request.POST.get('concepte', '')
        
        try:
            alumne = Alumne.objects.get(id=alumne_id)
            preu_final = (alumne.preu_per_hora or Decimal('0')) * hores
            
            # Record the payment
            PagamentAlumne.objects.create(
                alumne=alumne,
                data=date.today(),
                import_pagat=preu_final,
                concepte=f"Paga {hores}h: {concepte}",
                metode_pagament='Transferencia' # Default for now
            )
            messages.success(request, f"Gràcies! S'ha registrat un pagament de {preu_final}€ per a {alumne.nom}.")
            return redirect('home')
        except Alumne.DoesNotExist:
            messages.error(request, "Alumne no trobat.")
            
    alumnes = Alumne.objects.filter(actiu=True)
    return render(request, 'gestio/pagament_pares.html', {'alumnes': alumnes})

def logout_view(request):
    logout(request)
    return redirect('home')

def registro_alumne_view(request):
    if request.method == 'POST':
        form = AlumneRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumne registrat correctament!")
            return redirect('home')
    else:
        form = AlumneRegistrationForm()
    return render(request, 'gestio/registro_alumne.html', {'form': form})
