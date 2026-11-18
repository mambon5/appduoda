import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Professor, Classe, Alumne, PagamentAlumne, Materia

class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label="Codi de verificació", widget=forms.TextInput(attrs={'class': 'form-control'}))

class ProfessorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nom d'usuari")
    password = forms.CharField(widget=forms.PasswordInput, label="Contrasenya")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirma Contrasenya")
    materies = forms.ModelMultipleChoiceField(
        queryset=Materia.objects.all(),
        required=False,
        label="Matèries que pots impartir",
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )

    class Meta:
        model = Professor
        fields = ['nom', 'cognoms', 'email', 'telefon', 'adreca', 'materies']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les contrasenyes no coincideixen.")
        return cleaned_data

class ClasseForm(forms.ModelForm):
    alumnes = forms.ModelMultipleChoiceField(
        queryset=Alumne.objects.filter(actiu=True),
        label="Alumnes assistents",
        widget=forms.SelectMultiple(attrs={'class': 'select2', 'data-placeholder': 'Selecciona un o més alumnes'})
    )
    DURADA_CHOICES = [
        (30, '30 minuts'),
        (45, '45 minuts'),
        (60, '1 hora (60 min)'),
        (90, '1h 30m (90 min)'),
        (120, '2 hores (120 min)'),
    ]
    durada_minuts = forms.ChoiceField(
        choices=DURADA_CHOICES,
        initial=60,
        label="Durada",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data = forms.DateField(
        initial=datetime.date.today,
        label="Data",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    hora_inici = forms.TimeField(
        label="Hora d'inici",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = Classe
        fields = ['alumnes', 'data', 'hora_inici', 'durada_minuts', 'comentaris']
        widgets = {
            'comentaris': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Observacions o temari de la classe...'}),
        }

class AlumneRegistrationForm(forms.ModelForm):
    materies = forms.ModelMultipleChoiceField(
        queryset=Materia.objects.all(),
        required=False,
        label="Matèries de reforç",
        widget=forms.SelectMultiple(attrs={'class': 'select2', 'data-placeholder': 'Selecciona les matèries'})
    )

    class Meta:
        model = Alumne
        fields = ['nom', 'cognoms', 'curs', 'materies', 'telefon', 'nom_pare', 'telefon_pare', 'email_pare', 'adreca', 'nom_centre']
        widgets = {
            'curs': forms.Select(attrs={'class': 'form-control'}),
        }

class PagamentAlumneForm(forms.ModelForm):
    alumnes = forms.ModelMultipleChoiceField(
        queryset=Alumne.objects.filter(actiu=True),
        label="Alumne(s)",
        widget=forms.SelectMultiple(attrs={'class': 'select2', 'data-placeholder': 'Tria un o diversos alumnes (ex: germans)'})
    )
    data = forms.DateField(
        initial=datetime.date.today,
        label="Data del pagament",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = PagamentAlumne
        fields = ['alumnes', 'data', 'tipus_pack', 'hores_pagades', 'import_pagat', 'metode_pagament', 'concepte']
        widgets = {
            'tipus_pack': forms.Select(attrs={'id': 'id_tipus_pack', 'class': 'form-control'}),
            'hores_pagades': forms.NumberInput(attrs={'id': 'id_hores_pagades', 'step': '0.5', 'class': 'form-control'}),
            'import_pagat': forms.NumberInput(attrs={'id': 'id_import_pagat', 'step': '0.01', 'class': 'form-control'}),
            'metode_pagament': forms.Select(attrs={'class': 'form-control'}),
            'concepte': forms.TextInput(attrs={'placeholder': "Ex: Mensualitat abril", 'class': 'form-control'}),
        }

# Retenim PagamentPareForm com a alias per retrocompatibilitat si calgués
PagamentPareForm = PagamentAlumneForm
