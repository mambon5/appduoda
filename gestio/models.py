from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Materia(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Matèria"
        verbose_name_plural = "Matèries"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Alumne(models.Model):
    CURSOS = [
        # Primària
        ('1PRI', '1r de Primària'),
        ('2PRI', '2n de Primària'),
        ('3PRI', '3r de Primària'),
        ('4PRI', '4t de Primària'),
        ('5PRI', '5è de Primària'),
        ('6PRI', '6è de Primària'),
        # ESO
        ('1ESO', "1r d'ESO"),
        ('2ESO', "2n d'ESO"),
        ('3ESO', "3r d'ESO"),
        ('4ESO', "4t d'ESO"),
        # Batxillerat i Universitat
        ('1BATX', '1r de Batxillerat'),
        ('2BATX', '2n de Batxillerat'),
        ('UNI', 'Universitat'),
    ]
    nom = models.CharField(max_length=100)
    cognoms = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    nom_pare = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nom pare/mare")
    telefon_pare = models.CharField(max_length=20, blank=True, null=True)
    email_pare = models.EmailField(blank=True, null=True, verbose_name="Email pare/mare")
    adreca = models.CharField(max_length=255, blank=True, null=True)
    nom_centre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Escola/Centre")
    curs = models.CharField(max_length=20, choices=CURSOS, default='ESO')
    materies = models.ManyToManyField(Materia, blank=True)
    preu_per_hora = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actiu = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Alumne"
        verbose_name_plural = "Alumnes"

    def __str__(self):
        return f"{self.nom} {self.cognoms} ({self.get_curs_display()})"

    @property
    def total_hores_pagades(self):
        return sum([p.hores_pagades for p in self.pagaments.all()]) or Decimal('0.00')

    @property
    def total_hores_fetes(self):
        return sum([Decimal(str(c.durada_minuts / 60)) for c in self.classes.all()]) or Decimal('0.00')

    @property
    def saldo_hores(self):
        return round(float(self.total_hores_pagades - self.total_hores_fetes), 2)

    @property
    def saldo(self):
        return self.saldo_hores

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile', null=True, blank=True)
    nom = models.CharField(max_length=100)
    cognoms = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    adreca = models.CharField(max_length=255, blank=True, null=True)
    materies = models.ManyToManyField(Materia, blank=True)
    
    # Trams de preus per hora segons nº d'alumnes
    preu_1_alumne = models.DecimalField(max_digits=5, decimal_places=2, default=12.00)
    preu_2_alumnes = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    preu_3_alumnes = models.DecimalField(max_digits=5, decimal_places=2, default=21.00)
    preu_4_alumnes = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    preu_5_mes_alumnes = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professors"

    def get_preu_hora(self, num_alumnes):
        trams = {
            1: self.preu_1_alumne,
            2: self.preu_2_alumnes,
            3: self.preu_3_alumnes,
            4: self.preu_4_alumnes,
        }
        return trams.get(num_alumnes, self.preu_5_mes_alumnes) if num_alumnes > 0 else Decimal('0.00')

    def __str__(self):
        return f"{self.nom} {self.cognoms}"

class Classe(models.Model):
    data = models.DateField()
    hora_inici = models.TimeField()
    durada_minuts = models.PositiveIntegerField(default=60)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='classes')
    alumnes = models.ManyToManyField(Alumne, related_name='classes')
    comentaris = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

    @property
    def cost_professor(self):
        hores = self.durada_minuts / 60
        return round(float(self.professor.get_preu_hora(self.alumnes.count())) * hores, 2)

    def __str__(self):
        return f"{self.data} - {self.professor} ({self.alumnes.count()} alumnes)"

class PagamentAlumne(models.Model):
    PACKS = [
        ('4', 'Mensual 1h/setmana (4h)'),
        ('8', 'Mensual 2h/setmana (8h)'),
        ('12', 'Mensual 3h/setmana (12h)'),
        ('ALTRES', 'Hores soltes / Personalitzat'),
    ]
    alumnes = models.ManyToManyField(Alumne, related_name='pagaments')
    recaudador = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='pagaments_recollits', null=True, blank=True)
    data = models.DateField()
    tipus_pack = models.CharField(max_length=10, choices=PACKS, default='4')
    hores_pagades = models.DecimalField(max_digits=5, decimal_places=2, default=4.00, help_text="Total d'hores que cobreix aquest pagament")
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pagament = models.CharField(max_length=50, choices=[('Efectiu', 'Efectiu'), ('Transferencia', 'Transferència'), ('Bizum', 'Bizum')], default='Efectiu')
    concepte = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Pagament Alumne"
        verbose_name_plural = "Pagaments Alumnes"

    def __str__(self):
        noms = ", ".join([a.nom for a in self.alumnes.all()])
        return f"{noms} - {self.import_pagat}€ ({self.hores_pagades}h)"

class PagamentProfessor(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='pagaments_rebuts')
    data = models.DateField()
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2)
    concepte = models.CharField(max_length=255, blank=True, null=True)
    metode_pagament = models.CharField(max_length=50, choices=[('Efectiu', 'Efectiu'), ('Transferencia', 'Transferència'), ('Bizum', 'Bizum')], default='Efectiu')

    class Meta:
        verbose_name = "Pagament Professor"
        verbose_name_plural = "Pagaments Professors"

    def __str__(self):
        return f"Pagament a Prof. {self.professor} - {self.import_pagat}€ ({self.data})"
