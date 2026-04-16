from django.contrib import admin
from .models import Alumne, Professor, Classe, PagamentAlumne, PagamentProfessor

@admin.register(Alumne)
class AlumneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'cognoms', 'email', 'telefon', 'actiu')
    search_fields = ('nom', 'cognoms', 'email')
    list_filter = ('actiu',)

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nom', 'cognoms', 'email', 'telefon', 'preu_hora')
    search_fields = ('nom', 'cognoms', 'email')

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('data', 'hora_inici', 'durada_minuts', 'alumne', 'professor', 'preu_classe')
    list_filter = ('data', 'professor', 'alumne')
    search_fields = ('alumne__nom', 'professor__nom', 'comentaris')
    date_hierarchy = 'data'

@admin.register(PagamentAlumne)
class PagamentAlumneAdmin(admin.ModelAdmin):
    list_display = ('alumne', 'data', 'import_pagat', 'metode_pagament', 'concepte')
    list_filter = ('data', 'metode_pagament', 'alumne')
    search_fields = ('alumne__nom', 'concepte')
    date_hierarchy = 'data'

@admin.register(PagamentProfessor)
class PagamentProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'data', 'import_pagat', 'metode_pagament', 'concepte')
    list_filter = ('data', 'metode_pagament', 'professor')
    search_fields = ('professor__nom', 'concepte')
    date_hierarchy = 'data'
