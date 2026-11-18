from django.contrib import admin
from .models import Materia, Alumne, Professor, Classe, PagamentAlumne, PagamentProfessor

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Alumne)
class AlumneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'cognoms', 'curs', 'telefon', 'nom_pare', 'telefon_pare', 'preu_per_hora', 'saldo_hores', 'actiu')
    list_filter = ('actiu', 'curs')
    search_fields = ('nom', 'cognoms', 'nom_pare', 'telefon', 'telefon_pare')
    filter_horizontal = ('materies',)

    def saldo_hores(self, obj):
        return f"{obj.saldo_hores} h"
    saldo_hores.short_description = "Saldo (h)"

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nom', 'cognoms', 'user', 'email', 'telefon', 'preu_1_alumne', 'preu_2_alumnes', 'preu_3_alumnes', 'preu_4_alumnes', 'preu_5_mes_alumnes')
    search_fields = ('nom', 'cognoms', 'email', 'user__username')
    filter_horizontal = ('materies',)

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('data', 'hora_inici', 'durada_minuts', 'professor', 'display_alumnes', 'num_alumnes', 'cost_professor')
    list_filter = ('data', 'professor')
    search_fields = ('professor__nom', 'professor__cognoms', 'alumnes__nom', 'alumnes__cognoms', 'comentaris')
    filter_horizontal = ('alumnes',)
    date_hierarchy = 'data'

    def display_alumnes(self, obj):
        return ", ".join([f"{a.nom} {a.cognoms}" for a in obj.alumnes.all()])
    display_alumnes.short_description = "Alumnes"

    def num_alumnes(self, obj):
        return obj.alumnes.count()
    num_alumnes.short_description = "Nº Alumnes"

    def cost_professor(self, obj):
        return f"{obj.cost_professor} €"
    cost_professor.short_description = "Cost Professor"

@admin.register(PagamentAlumne)
class PagamentAlumneAdmin(admin.ModelAdmin):
    list_display = ('display_alumnes', 'data', 'tipus_pack', 'hores_pagades', 'import_pagat', 'metode_pagament', 'recaudador')
    list_filter = ('data', 'tipus_pack', 'metode_pagament')
    search_fields = ('alumnes__nom', 'alumnes__cognoms', 'concepte')
    filter_horizontal = ('alumnes',)
    date_hierarchy = 'data'

    def display_alumnes(self, obj):
        return ", ".join([f"{a.nom} {a.cognoms}" for a in obj.alumnes.all()])
    display_alumnes.short_description = "Alumnes"

@admin.register(PagamentProfessor)
class PagamentProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'data', 'import_pagat', 'metode_pagament', 'concepte')
    list_filter = ('data', 'metode_pagament', 'professor')
    search_fields = ('professor__nom', 'concepte')
    date_hierarchy = 'data'
