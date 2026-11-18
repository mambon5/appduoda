from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from decimal import Decimal
import datetime
from gestio.models import Materia, Alumne, Professor, Classe, PagamentAlumne, PagamentProfessor
from gestio.forms import ClasseForm, PagamentAlumneForm

class ModelAndBusinessLogicTests(TestCase):
    def setUp(self):
        # Matèries
        self.mat_mates = Materia.objects.create(nom="Matemàtiques")
        self.mat_angles = Materia.objects.create(nom="Anglès")

        # Alumnes
        self.alumne1 = Alumne.objects.create(
            nom="Marc",
            cognoms="Soler",
            curs="ESO",
            nom_pare="Joan Soler",
            telefon_pare="600111222",
            preu_per_hora=Decimal('15.00')
        )
        self.alumne1.materies.add(self.mat_mates)

        self.alumne2 = Alumne.objects.create(
            nom="Laia",
            cognoms="Soler",
            curs="1BATX",
            nom_pare="Joan Soler",
            telefon_pare="600111222",
            preu_per_hora=Decimal('18.00')
        )
        self.alumne2.materies.add(self.mat_mates, self.mat_angles)

        # Professor amb preus per defecte (12, 16, 21, 25, 25)
        self.user_prof = User.objects.create_user(username="prof_anna", password="password123")
        self.professor = Professor.objects.create(
            user=self.user_prof,
            nom="Anna",
            cognoms="Vidal",
            email="anna@example.com",
            preu_1_alumne=Decimal('12.00'),
            preu_2_alumnes=Decimal('16.00'),
            preu_3_alumnes=Decimal('21.00'),
            preu_4_alumnes=Decimal('25.00'),
            preu_5_mes_alumnes=Decimal('25.00')
        )
        self.professor.materies.add(self.mat_mates)

    def test_materia_str(self):
        self.assertEqual(str(self.mat_mates), "Matemàtiques")

    def test_alumne_str_and_curs(self):
        self.assertEqual(str(self.alumne1), "Marc Soler (ESO)")
        self.assertEqual(str(self.alumne2), "Laia Soler (1r Batxillerat)")

    def test_professor_get_preu_hora(self):
        self.assertEqual(self.professor.get_preu_hora(1), Decimal('12.00'))
        self.assertEqual(self.professor.get_preu_hora(2), Decimal('16.00'))
        self.assertEqual(self.professor.get_preu_hora(3), Decimal('21.00'))
        self.assertEqual(self.professor.get_preu_hora(4), Decimal('25.00'))
        self.assertEqual(self.professor.get_preu_hora(6), Decimal('25.00'))
        self.assertEqual(self.professor.get_preu_hora(0), Decimal('0.00'))

    def test_classe_cost_professor(self):
        # Classe de 60 min amb 1 alumne -> 12€
        c1 = Classe.objects.create(
            data=datetime.date.today(),
            hora_inici=datetime.time(16, 0),
            durada_minuts=60,
            professor=self.professor
        )
        c1.alumnes.add(self.alumne1)
        self.assertEqual(c1.cost_professor, 12.0)

        # Classe de 90 minuts amb 2 alumnes -> 16€ * 1.5h = 24€
        c2 = Classe.objects.create(
            data=datetime.date.today(),
            hora_inici=datetime.time(17, 30),
            durada_minuts=90,
            professor=self.professor
        )
        c2.alumnes.add(self.alumne1, self.alumne2)
        self.assertEqual(c2.cost_professor, 24.0)

    def test_pagament_alumne_and_saldo(self):
        # Pagament pack 8h compartit entre germans
        p1 = PagamentAlumne.objects.create(
            data=datetime.date.today(),
            tipus_pack='8',
            hores_pagades=Decimal('8.00'),
            import_pagat=Decimal('120.00'),
            metode_pagament='Transferencia'
        )
        p1.alumnes.add(self.alumne1, self.alumne2)

        # Abans de classes, alumne1 té 8h pagades i 0h fetes -> saldo 8h
        self.assertEqual(self.alumne1.total_hores_pagades, Decimal('8.00'))
        self.assertEqual(self.alumne1.total_hores_fetes, Decimal('0.00'))
        self.assertEqual(self.alumne1.saldo_hores, 8.0)

        # Fer 1 classe de 60 min (1h)
        c1 = Classe.objects.create(
            data=datetime.date.today(),
            hora_inici=datetime.time(16, 0),
            durada_minuts=60,
            professor=self.professor
        )
        c1.alumnes.add(self.alumne1)

        # Saldo restant: 8h - 1h = 7.0h
        self.assertEqual(self.alumne1.total_hores_fetes, Decimal('1.00'))
        self.assertEqual(self.alumne1.saldo_hores, 7.0)

    def test_classe_form_validation(self):
        form_data = {
            'alumnes': [self.alumne1.pk, self.alumne2.pk],
            'data': datetime.date.today(),
            'hora_inici': '17:00',
            'durada_minuts': 60,
            'comentaris': 'Repàs examen de funcions'
        }
        form = ClasseForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_pagament_form_validation(self):
        form_data = {
            'alumnes': [self.alumne1.pk],
            'data': datetime.date.today(),
            'tipus_pack': '4',
            'hores_pagades': '4.00',
            'import_pagat': '60.00',
            'metode_pagament': 'Bizum',
            'concepte': 'Mensualitat Novembre'
        }
        form = PagamentAlumneForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_command_crear_materies(self):
        call_command('crear_materies')
        self.assertTrue(Materia.objects.filter(nom="Física").exists())
        self.assertTrue(Materia.objects.filter(nom="Química").exists())
        self.assertTrue(Materia.objects.filter(nom="Filosofia").exists())
