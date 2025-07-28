from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with custom User model'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email address')
        parser.add_argument('--password', type=str, required=True, help='Password')
        parser.add_argument('--full-name', type=str, required=True, help='Full name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        full_name = options['full_name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return

        # Create superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            role='superadmin'
        )

        # Update profile
        if hasattr(user, 'profile'):
            user.profile.full_name = full_name
            user.profile.save()

        self.stdout.write(
            self.style.SUCCESS(f'Superuser {email} created successfully')
        ) 