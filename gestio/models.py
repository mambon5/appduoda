from django.db import models
from django.contrib.auth.models import User

class Alumne(models.Model):
    nom = models.CharField(max_length=100)
    cognoms = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    adreca = models.CharField(max_length=255, blank=True, null=True)
    telefon_pare = models.CharField(max_length=20, blank=True, null=True)
    email_pare = models.EmailField(blank=True, null=True)
    nom_centre = models.CharField(max_length=100, blank=True, null=True)
    preu_per_hora = models.DecimalField(max_digits=5, decimal_places=2, help_text="Preu per hora que paga aquest alumne", null=True, blank=True)
    actiu = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} {self.cognoms}"

    class Meta:
        verbose_name = "Alumne"
        verbose_name_plural = "Alumnes"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile', null=True, blank=True)
    nom = models.CharField(max_length=100)
    cognoms = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    preu_hora = models.DecimalField(max_digits=5, decimal_places=2, help_text="Preu que cobra el profe per hora")

    def __str__(self):
        return f"{self.nom} {self.cognoms}"

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professors"

class Classe(models.Model):
    data = models.DateField()
    hora_inici = models.TimeField()
    durada_minuts = models.PositiveIntegerField(default=60)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='classes')
    alumne = models.ForeignKey(Alumne, on_delete=models.CASCADE, related_name='classes')
    preu_classe = models.DecimalField(max_digits=6, decimal_places=2, help_text="Preu que paga l'alumne per aquesta classe")
    comentaris = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Classe {self.data} - {self.alumne} amb {self.professor}"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

class PagamentAlumne(models.Model):
    alumne = models.ForeignKey(Alumne, on_delete=models.CASCADE, related_name='pagaments')
    data = models.DateField()
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2)
    concepte = models.CharField(max_length=255, blank=True, null=True)
    metode_pagament = models.CharField(max_length=50, choices=[('Efectiu', 'Efectiu'), ('Transferencia', 'Transferència'), ('Bizum', 'Bizum')], default='Efectiu')

    def __str__(self):
        return f"Pagament {self.alumne} - {self.import_pagat}€ ({self.data})"

    class Meta:
        verbose_name = "Pagament Alumne"
        verbose_name_plural = "Pagaments Alumnes"

class PagamentProfessor(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='pagaments_rebuts')
    data = models.DateField()
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2)
    concepte = models.CharField(max_length=255, blank=True, null=True)
    metode_pagament = models.CharField(max_length=50, choices=[('Efectiu', 'Efectiu'), ('Transferencia', 'Transferència'), ('Bizum', 'Bizum')], default='Efectiu')

    def __str__(self):
        return f"Pagament a Prof. {self.professor} - {self.import_pagat}€ ({self.data})"

    class Meta:
        verbose_name = "Pagament Professor"
        verbose_name_plural = "Pagaments Professors"
