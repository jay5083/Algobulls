from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def home(request):
    # Fetch AlgobullsEmployee object corresponding to the currently logged-in user's email address

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())

    # Print all permissions on the terminal
    
    
    
    
    user_group = user_groups[0].name  # Fetch the name of the first user group
    # Pass user groups, user permissions, and employee ID to the template context
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        "role_name": user_group,  # Replace "Sales Head" with user_group
        
    }

    return render(request, 'base.html', context)