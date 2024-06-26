# your_app/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import AuthPermission, AlgobullsDivision, Branch, AlgobullsEmployee, BranchEmployee  # Ensure you import necessary models

class CustomUserForm(forms.ModelForm):
    EMPLOYEE_CHOICES = (
        ('Algobulls Employee', 'Algobulls Employee'),
        ('Branch Employee', 'Branch Employee'),
    )

    employee_type = forms.ChoiceField(choices=EMPLOYEE_CHOICES, required=True)
    division_name = forms.ModelChoiceField(queryset=AlgobullsDivision.objects.all(), required=False)
    branch_id = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False)

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check if a User instance is being edited
        if self.instance.pk:
            try:
                # Fetch the AuthPermission entry for the current user
                auth_permission = AuthPermission.objects.get(user=self.instance)
                self.fields['employee_type'].initial = auth_permission.employee_type

                if auth_permission.employee_type == 'Algobulls Employee':
                    algobulls_employee = AlgobullsEmployee.objects.get(employee_id=self.instance.pk)
                    self.fields['division_name'].initial = algobulls_employee.division_name
                elif auth_permission.employee_type == 'Branch Employee':
                    branch_employee = BranchEmployee.objects.get(branch_employee_id=self.instance.pk)
                    self.fields['branch_id'].initial = branch_employee.branch_id
            except (AuthPermission.DoesNotExist, AlgobullsEmployee.DoesNotExist, BranchEmployee.DoesNotExist):
                self.fields['employee_type'].initial = None  # Set to None if no entry found

