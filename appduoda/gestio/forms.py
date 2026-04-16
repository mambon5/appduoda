from django import forms
from django.contrib.auth.models import User
from .models import Professor, Classe, Alumne, PagamentAlumne

class ProfessorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Professor
        fields = ['nom', 'cognoms', 'email', 'telefon', 'preu_hora']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les contrasenyes no coincideixen.")
        return cleaned_data

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['data', 'hora_inici', 'durada_minuts', 'alumne', 'preu_classe', 'comentaris']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inici': forms.TimeInput(attrs={'type': 'time'}),
        }

class AlumneRegistrationForm(forms.ModelForm):
    class Meta:
        model = Alumne
        fields = ['nom', 'cognoms', 'adreca', 'telefon_pare', 'email_pare', 'nom_centre']

class PagamentPareForm(forms.ModelForm):
    hores = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = PagamentAlumne
        fields = ['alumne', 'hores', 'concepte']
