from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from branches.models import Branch

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a new vendor with branch assignment'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Vendor name')
        parser.add_argument('--branch', type=str, required=True, help='Branch name')
        parser.add_argument('--contact-person', type=str, required=False, help='Contact person name')
        parser.add_argument('--phone', type=str, required=False, help='Phone number')
        parser.add_argument('--email', type=str, required=False, help='Email address')
        parser.add_argument('--address', type=str, required=False, help='Address')
        parser.add_argument('--vendor-type', type=str, default='supplier', 
                          choices=['supplier', 'service_provider', 'contractor', 'other'],
                          help='Vendor type')
        parser.add_argument('--manager-email', type=str, required=False, help='Manager email for assignment')

    def handle(self, *args, **options):
        name = options['name']
        branch_name = options['branch']
        contact_person = options.get('contact_person', '')
        phone = options.get('phone', '')
        email = options.get('email', '')
        address = options.get('address', '')
        vendor_type = options['vendor_type']
        manager_email = options.get('manager_email')

        # Get branch
        try:
            branch = Branch.objects.get(name=branch_name)
        except Branch.DoesNotExist:
            raise CommandError(f'Branch "{branch_name}" does not exist')

        # Check if vendor already exists in this branch
        if Vendor.objects.filter(name=name, branch=branch).exists():
            self.stdout.write(
                self.style.WARNING(f'Vendor "{name}" already exists in branch "{branch_name}"')
            )
            return

        # Get manager if provided
        added_by = None
        if manager_email:
            try:
                manager = User.objects.get(email=manager_email, role='manager')
                if hasattr(manager, 'managed_branch') and manager.managed_branch == branch:
                    added_by = manager
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Manager {manager_email} is not assigned to branch "{branch_name}"')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Manager {manager_email} not found or not a manager')
                )

        # Create vendor
        vendor = Vendor.objects.create(
            name=name,
            branch=branch,
            contact_person=contact_person,
            phone_number=phone,
            email=email,
            address=address,
            vendor_type=vendor_type,
            added_by=added_by
        )

        self.stdout.write(
            self.style.SUCCESS(f'Vendor "{name}" created successfully in branch "{branch_name}"')
        ) 