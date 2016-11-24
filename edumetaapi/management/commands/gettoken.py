from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or get token for username'

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['user']:
            try:
                token = Token.objects.get_or_create(user=User.objects.get(username=username))
            except User.DoesNotExist as e:
                self.stdout.write(self.style.ERROR('Unknown username \'{}\''.format(username)))
            else:
                self.stdout.write('{}: {}'.format(username, token[0].key))
