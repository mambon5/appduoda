from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Professor, Classe, Alumne, PagamentAlumne
from .forms import ProfessorRegistrationForm, ClasseForm, PagamentPareForm, AlumneRegistrationForm, EmailVerificationForm
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
import random

def home(request):
    return render(request, 'gestio/home.html')

def serialize_data(cleaned_data):
    serialized = {}
    for k, v in cleaned_data.items():
        if isinstance(v, Decimal):
            serialized[k] = str(v)
        elif isinstance(v, date):
            serialized[k] = v.isoformat()
        else:
            serialized[k] = v
    return serialized

def send_verification_email(email, code):
    subject = "Codi de verificació per al registre"
    message = f"El teu codi de verificació és: {code}"
    send_mail(subject, message, None, [email], fail_silently=False)

def registro_profe_view(request):
    if request.method == 'POST':
        form = ProfessorRegistrationForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            request.session['registration_data'] = serialize_data(form.cleaned_data)
            request.session['verification_code'] = code
            request.session['registration_type'] = 'profe'
            
            try:
                send_verification_email(form.cleaned_data['email'], code)
                messages.info(request, "T'hem enviat un correu amb el codi de verificació.")
                return redirect('verify_email')
            except Exception as e:
                messages.error(request, "Error enviant el correu electrònic.")
    else:
        form = ProfessorRegistrationForm()
    return render(request, 'gestio/registro_profe.html', {'form': form})

def registro_alumne_view(request):
    if request.method == 'POST':
        form = AlumneRegistrationForm(request.POST)
        if form.is_valid():
            code = str(random.randint(100000, 999999))
            request.session['registration_data'] = serialize_data(form.cleaned_data)
            request.session['verification_code'] = code
            request.session['registration_type'] = 'alumne'
            
            try:
                send_verification_email(form.cleaned_data['email_pare'], code)
                messages.info(request, "T'hem enviat un correu amb el codi de verificació al email del pare/mare.")
                return redirect('verify_email')
            except Exception as e:
                messages.error(request, "Error enviant el correu electrònic.")
    else:
        form = AlumneRegistrationForm()
    return render(request, 'gestio/registro_alumne.html', {'form': form})

def verify_email_view(request):
    registration_data = request.session.get('registration_data')
    verification_code = request.session.get('verification_code')
    registration_type = request.session.get('registration_type')

    if not registration_data or not verification_code or not registration_type:
        messages.error(request, "Sessió de registre caducada o invàlida.")
        return redirect('home')

    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['code'] == verification_code:
                if registration_type == 'profe':
                    # Deserialitzar data per crear el Profe
                    user = User.objects.create_user(
                        username=registration_data['username'],
                        password=registration_data['password'],
                        email=registration_data['email']
                    )
                    professor = Professor(
                        user=user,
                        nom=registration_data['nom'],
                        cognoms=registration_data['cognoms'],
                        email=registration_data['email'],
                        telefon=registration_data['telefon'],
                        preu_hora=Decimal(registration_data['preu_hora']) if registration_data.get('preu_hora') else None
                    )
                    professor.save()
                    login(request, user)
                    messages.success(request, "Registre completat amb èxit!")
                    del request.session['registration_data']
                    del request.session['verification_code']
                    del request.session['registration_type']
                    return redirect('dashboard_profe')
                
                elif registration_type == 'alumne':
                    alumne = Alumne(
                        nom=registration_data['nom'],
                        cognoms=registration_data['cognoms'],
                        adreca=registration_data.get('adreca', ''),
                        telefon_pare=registration_data.get('telefon_pare', ''),
                        email_pare=registration_data.get('email_pare', ''),
                        nom_centre=registration_data.get('nom_centre', '')
                    )
                    alumne.save()
                    messages.success(request, "Alumne registrat correctament!")
                    del request.session['registration_data']
                    del request.session['verification_code']
                    del request.session['registration_type']
                    return redirect('home')
            else:
                messages.error(request, "Codi incorrecte.")
    else:
        form = EmailVerificationForm()
        
    return render(request, 'gestio/verify_email.html', {'form': form})

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
        hores = Decimal(request.POST.get('hores', '1'))
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
