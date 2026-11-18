from django.core.management.base import BaseCommand
from gestio.models import Materia

class Command(BaseCommand):
    help = "Crea les matèries inicials per defecte (Matemàtiques, Física, Química, Anglès, Català, etc.)"

    def handle(self, *args, **options):
        materies_inicials = [
            'Matemàtiques',
            'Física',
            'Química',
            'Anglès',
            'Català',
            'Castellà',
            'Biologia',
            'Història',
            'Geografia',
            'Filosofia',
            'Tecnologia',
            'Economia',
            'Reforç General'
        ]

        creades = 0
        for nom in materies_inicials:
            obj, created = Materia.objects.get_or_create(nom=nom)
            if created:
                creades += 1
                self.stdout.write(self.style.SUCCESS(f"Matèria creada: {nom}"))
            else:
                self.stdout.write(f"Matèria ja existent: {nom}")

        self.stdout.write(self.style.SUCCESS(f"Procés completat. {creades} matèries noves creades."))
