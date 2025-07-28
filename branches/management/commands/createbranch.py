from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from branches.models import Branch

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a new branch with optional manager assignment'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Branch name')
        parser.add_argument('--location', type=str, required=False, help='Branch location')
        parser.add_argument('--description', type=str, required=False, help='Branch description')
        parser.add_argument('--manager-email', type=str, required=False, help='Manager email')

    def handle(self, *args, **options):
        name = options['name']
        location = options.get('location', '')
        description = options.get('description', '')
        manager_email = options.get('manager_email')

        # Check if branch already exists
        if Branch.objects.filter(name=name).exists():
            raise CommandError(f'Branch "{name}" already exists')

        # Create branch
        branch = Branch.objects.create(
            name=name,
            location=location,
            description=description
        )

        # Assign manager if provided
        if manager_email:
            try:
                manager = User.objects.get(email=manager_email, role='manager')
                
                # Check if manager is already assigned to another branch
                if hasattr(manager, 'managed_branch') and manager.managed_branch:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Manager {manager_email} is already managing branch "{manager.managed_branch.name}"'
                        )
                    )
                else:
                    branch.assign_manager(manager)
                    self.stdout.write(
                        self.style.SUCCESS(f'Manager {manager_email} assigned to branch "{name}"')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'User {manager_email} not found or not a manager')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Branch "{name}" created successfully')
        ) 