# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def selectedOption(division_employee_division_name, support_division_name):
    print(f"Comparing {division_employee_division_name} with {support_division_name}")
    return division_employee_division_name == support_division_name
