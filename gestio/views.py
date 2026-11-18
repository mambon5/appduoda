from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum, QuerySet
from .models import Professor, Classe, Alumne, PagamentAlumne, Materia
from .forms import ProfessorRegistrationForm, ClasseForm, PagamentAlumneForm, AlumneRegistrationForm, EmailVerificationForm
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
        elif isinstance(v, QuerySet) or (hasattr(v, '__iter__') and not isinstance(v, (str, bytes, dict))):
            serialized[k] = [item.pk if hasattr(item, 'pk') else item for item in v]
        else:
            serialized[k] = v
    return serialized

def send_verification_email(email, code):
    subject = "Codi de verificació per al registre - Duoda"
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
                # Si falla l'enviament per configuració SMTP local, mostrem avís o procedim
                messages.error(request, f"Error enviant el correu electrònic: {e}")
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
            
            email_desti = form.cleaned_data.get('email_pare') or form.cleaned_data.get('email')
            if email_desti:
                try:
                    send_verification_email(email_desti, code)
                    messages.info(request, "T'hem enviat un correu amb el codi de verificació al email del pare/mare.")
                    return redirect('verify_email')
                except Exception as e:
                    messages.error(request, f"Error enviant el correu electrònic: {e}")
            else:
                # Si no s'ha introduït correu, es crea directament
                alumne = form.save()
                messages.success(request, f"Alumne {alumne.nom} registrat correctament!")
                return redirect('home')
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
                    user = User.objects.create_user(
                        username=registration_data['username'],
                        password=registration_data['password'],
                        email=registration_data.get('email', '')
                    )
                    professor = Professor.objects.create(
                        user=user,
                        nom=registration_data['nom'],
                        cognoms=registration_data['cognoms'],
                        email=registration_data.get('email', ''),
                        telefon=registration_data.get('telefon', ''),
                        adreca=registration_data.get('adreca', ''),
                    )
                    if registration_data.get('materies'):
                        professor.materies.set(registration_data['materies'])

                    login(request, user)
                    messages.success(request, "Registre de professor completat amb èxit!")
                    del request.session['registration_data']
                    del request.session['verification_code']
                    del request.session['registration_type']
                    return redirect('dashboard_profe')
                
                elif registration_type == 'alumne':
                    alumne = Alumne.objects.create(
                        nom=registration_data['nom'],
                        cognoms=registration_data['cognoms'],
                        curs=registration_data.get('curs', 'ESO'),
                        telefon=registration_data.get('telefon', ''),
                        nom_pare=registration_data.get('nom_pare', ''),
                        telefon_pare=registration_data.get('telefon_pare', ''),
                        email_pare=registration_data.get('email_pare', ''),
                        adreca=registration_data.get('adreca', ''),
                        nom_centre=registration_data.get('nom_centre', '')
                    )
                    if registration_data.get('materies'):
                        alumne.materies.set(registration_data['materies'])

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
            form.save_m2m()
            messages.success(request, f"Classe registrada correctament. Cobrament calculat: {classe.cost_professor}€ ({classe.alumnes.count()} alumnes).")
            return redirect('dashboard_profe')
    else:
        form = ClasseForm()

    classes = Classe.objects.filter(professor=professor).prefetch_related('alumnes').order_by('-data', '-hora_inici')
    return render(request, 'gestio/dashboard_profe.html', {
        'form': form,
        'professor': professor,
        'classes': classes
    })

def pagament_pares_view(request):
    if request.method == 'POST':
        form = PagamentAlumneForm(request.POST)
        if form.is_valid():
            pagament = form.save(commit=False)
            if request.user.is_authenticated:
                pagament.recaudador = request.user
            pagament.save()
            form.save_m2m()
            alumnes_noms = ", ".join([a.nom for a in pagament.alumnes.all()])
            messages.success(request, f"Gràcies! Pagament de {pagament.import_pagat}€ ({pagament.hores_pagades}h) registrat correctament per a: {alumnes_noms}.")
            return redirect('home')
    else:
        form = PagamentAlumneForm()

    alumnes = Alumne.objects.filter(actiu=True)
    return render(request, 'gestio/pagament_pares.html', {
        'form': form,
        'alumnes': alumnes
    })

@login_required
def liquidacio_view(request):
    if not request.user.is_staff:
        messages.error(request, "No tens permís per veure les liquidacions.")
        return redirect('home')

    # 1. Total diners recollits per cada Recaudador
    recaudacions = PagamentAlumne.objects.values('recaudador__username').annotate(
        total_recollit=Sum('import_pagat')
    )
    total_recaptat = PagamentAlumne.objects.aggregate(Sum('import_pagat'))['import_pagat__sum'] or Decimal('0.00')

    # 2. Total diners que corresponen a cada Professor segons assistents a cada classe
    professors = Professor.objects.all()
    resum_professors = []
    total_cost_professors = Decimal('0.00')

    for prof in professors:
        classes_prof = Classe.objects.filter(professor=prof).prefetch_related('alumnes')
        cost_total = Decimal(str(sum(c.cost_professor for c in classes_prof)))
        total_cost_professors += cost_total

        # Pagaments ja fets al professor
        pagat_prof = prof.pagaments_rebuts.aggregate(Sum('import_pagat'))['import_pagat__sum'] or Decimal('0.00')
        pendent_pagar = cost_total - pagat_prof

        resum_professors.append({
            'professor': prof,
            'num_classes': classes_prof.count(),
            'import_profe': cost_total,
            'pagat_prof': pagat_prof,
            'pendent_pagar': pendent_pagar,
        })

    marge_net = total_recaptat - total_cost_professors

    return render(request, 'gestio/liquidacio.html', {
        'recaudacions': recaudacions,
        'resum_professors': resum_professors,
        'total_recaptat': total_recaptat,
        'total_cost_professors': total_cost_professors,
        'marge_net': marge_net,
    })

def logout_view(request):
    logout(request)
    return redirect('home')
