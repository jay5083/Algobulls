from django.contrib import admin
from .models import AlgobullsDivision, AlgobullsEmployee, AuthPermission, AuthRole, Branch, BranchEmployee, Broker, Build, PermissionAccessTable, Sales, Strategies, Support, TechTask, Rms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

admin.site.register(AlgobullsDivision)
admin.site.register(AlgobullsEmployee)
admin.site.register(AuthPermission)
admin.site.register(AuthRole)
admin.site.register(Branch)
admin.site.register(BranchEmployee)
admin.site.register(Broker)
admin.site.register(Build)
admin.site.register(PermissionAccessTable)
admin.site.register(Sales)
admin.site.register(Strategies)
admin.site.register(Support)
admin.site.register(TechTask)
admin.site.register(Rms)

# your_app/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .forms import CustomUserForm
from .models import AlgobullsEmployee, BranchEmployee, AuthPermission, AlgobullsDivision, Branch

class CustomUserAdmin(DefaultUserAdmin):
    form = CustomUserForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'employee_type', 'division_name', 'branch_id')}),  # Add the new fields
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        employee_type = form.cleaned_data.get('employee_type')
        division_name = form.cleaned_data.get('division_name')
        branch_id = form.cleaned_data.get('branch_id')

        super().save_model(request, obj, form, change)

        if not change:  # Only handle creation
            if employee_type == 'Algobulls Employee':
                AlgobullsEmployee.objects.update_or_create(
                    employee_id=obj.id,
                    defaults={
                        'email_id': obj.email,
                        'password': obj.password,
                        'name': f"{obj.first_name} {obj.last_name}",
                        'division_name': division_name,  # Save division name
                        # Add additional fields here if needed
                    }
                )
            elif employee_type == 'Branch Employee':
                BranchEmployee.objects.update_or_create(
                    branch_employee_id=obj.id,
                    defaults={
                        'email_id': obj.email,
                        'password': obj.password,
                        'name': f"{obj.first_name} {obj.last_name}",
                        'branch_id': branch_id,  # Save branch ID
                        # Add additional fields here if needed
                    }
                )

        # Handle AuthPermission creation or update
        AuthPermission.objects.update_or_create(
            user=obj,
            defaults={
                'employee_type': employee_type,
            }
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if change:  # Only handle updates
            user = form.instance
            employee_type = form.cleaned_data.get('employee_type')
            division_name = form.cleaned_data.get('division_name')
            branch_id = form.cleaned_data.get('branch_id')

            if employee_type == 'Algobulls Employee':
                AlgobullsEmployee.objects.update_or_create(
                    employee_id=user.id,
                    defaults={
                        'email_id': user.email,
                        'password': user.password,
                        'name': f"{user.first_name} {user.last_name}",
                        'division_name': division_name,  # Save division name
                        # Add additional fields here if needed
                    }
                )
                # Delete BranchEmployee record if it exists
                BranchEmployee.objects.filter(branch_employee_id=user.id).delete()
            elif employee_type == 'Branch Employee':
                BranchEmployee.objects.update_or_create(
                    branch_employee_id=user.id,
                    defaults={
                        'email_id': user.email,
                        'password': user.password,
                        'name': f"{user.first_name} {user.last_name}",
                        'branch_id': branch_id,  # Save branch ID
                        # Add additional fields here if needed
                    }
                )
                # Delete AlgobullsEmployee record if it exists
                AlgobullsEmployee.objects.filter(employee_id=user.id).delete()

            # Update AuthPermission
            AuthPermission.objects.update_or_create(
                user=user,
                defaults={
                    'employee_type': employee_type,
                }
            )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
