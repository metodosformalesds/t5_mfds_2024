import random
from django.core.management.base import BaseCommand
from apps.appUser.models import Client


class Command(BaseCommand):
    """
    Author: Santiago Mendivil
    Command to assign unique identifiers to users who do not have one.
    This command filters all users in the Client model who have a null 'identificator' field
    and assigns them a random identifier between 100000 and 999999. The identifier is then
    saved to the user record, and a success message is printed to the console for each user.
    Methods:
        handle(self, *args, **kwargs): Main method that executes the command logic.
    """
    help = 'Asigna identificadores a todos los usuarios que no tienen uno'

    def handle(self, *args, **kwargs):
        users = Client.objects.filter(identificator__isnull=True)
        for user in users:
            user.identificator = random.randint(100000, 999999)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Identificador asignado a {user.id}'))
