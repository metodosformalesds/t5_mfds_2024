import random
from django.core.management.base import BaseCommand
from apps.appUser.models import Client


class Command(BaseCommand):
    help = 'Asigna identificadores a todos los usuarios que no tienen uno'

    def handle(self, *args, **kwargs):
        users = Client.objects.filter(identificator__isnull=True)
        for user in users:
            user.identificator = random.randint(100000, 999999)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Identificador asignado a {user.id}'))
