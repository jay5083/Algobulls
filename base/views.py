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
from .models import AlgobullsEmployee, Sales, BranchEmployee, Build, TechTask, Support, Strategies
from datetime import datetime, date
from .models import Support, BranchEmployee, AlgobullsEmployee
from django.shortcuts import render, redirect

# Create your views here.
@login_required
def home(request):
    # Fetch AlgobullsEmployee object corresponding to the currently logged-in user's email address
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
    except AlgobullsEmployee.DoesNotExist:
        employee_id = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())

    # Print all permissions on the terminal
    
    
    sales_leads = Sales.objects.all().order_by('lead_id')
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    build = Build.objects.all()
    tech_task = TechTask.objects.all()
    support = Support.objects.all()
    strategies = Strategies.objects.all()
    name = algobulls_employee.name
    user_group = user_groups[0].name  # Fetch the name of the first user group
    # Pass user groups, user permissions, and employee ID to the template context
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'builds' : build,
        'tech_tasks' : tech_task,
        'supports' : support,
        'strategies' : strategies
    }

    return render(request, 'base.html', context)

def update_sales_leads(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for lead_id, lead_data in updated_data.items():
            try:
                lead = Sales.objects.get(lead_id=lead_id)
                for field, value in lead_data.items():
                    if field == 'branch_employee_id':
                        # Handle branch employee ID separately
                        try:
                            branch_employee = BranchEmployee.objects.get(employee_id=value)
                            setattr(lead, field, branch_employee)
                        except BranchEmployee.DoesNotExist:
                            # Handle the case where the provided branch employee ID does not exist
                            error_count += 1
                            continue  # Skip to the next iteration
                    elif field == 'sales_employee_id':
                        # Handle sales employee ID separately
                        try:
                            sales_employee = AlgobullsEmployee.objects.get(employee_id=value)
                            setattr(lead, field, sales_employee)
                        except AlgobullsEmployee.DoesNotExist:
                            # Handle the case where the provided sales employee ID does not exist
                            error_count += 1
                            continue  # Skip to the next iteration
                    else:
                        setattr(lead, field, value)
                lead.save()
                success_count += 1
            except Sales.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})

def add_sales_leads(request):
    if request.method == 'POST':
        # Extract form data
        lead_id = request.POST.get('lead_id')
        name = request.POST.get('name')
        email_id = request.POST.get('email_id')
        contact_number = request.POST.get('contact_number')
        branch_employee_id_id = request.POST.get('branch_employee_id')
        sales_employee_id = request.POST.get('sales_employee_id')
        broking_id = request.POST.get('broking_id')
        source_type = request.POST.get('source_type')
        category = request.POST.get('category')
        risk_appetite = request.POST.get('risk_appetite')
        comments = request.POST.get('comments')
        amount = request.POST.get('amount')
        status = request.POST.get('status')
        reason_for_dropped = request.POST.get('reason_for_dropped')

        # Validate and convert purchase_date format
        purchase_date= request.POST.get('purchase_date')
        # try:
        #     purchase_date = datetime.strptime(purchase_date_str, '%d-%m-%Y').date()
        # except ValueError:
        #     return JsonResponse({'error': 'Invalid date format for purchase_date'}, status=400)  # Redirect to an error page or handle the error appropriately

        print(branch_employee_id_id)
        # Check if the provided branch_employee_id exists
        if branch_employee_id_id:
            try:
                branch_employee = BranchEmployee.objects.get(branch_employee_id=branch_employee_id_id)
            except BranchEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            branch_employee = None


        # Check if the provided sales_employee_id exists
        if sales_employee_id:
            try:
                sales_employee = AlgobullsEmployee.objects.get(employee_id=sales_employee_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            sales_employee = None

        # Create a new SalesLead object and save it to the database
        new_lead = Sales.objects.create(
            lead_id=lead_id,
            name=name,
            email_id=email_id,
            contact_number=contact_number,
            branch_employee_id=branch_employee,
            sales_employee_id=sales_employee,
            broking_id=broking_id,
            source_type=source_type,
            category=category,
            risk_appetite=risk_appetite,
            comments=comments,
            amount=amount,
            purchase_date=purchase_date,
            status=status,
            reason_for_dropped=reason_for_dropped,
        )

        # Fetch Algobulls employee and user information
        
        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        branch_employees = BranchEmployee.objects.all()
        sales_employees = AlgobullsEmployee.objects.all()
        today_date = date.today()

        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'branch_employees': branch_employees,
            'sales_employees' : sales_employees,
            'today_date': today_date,
        }

        return render(request, 'add_sales_leads.html', context)
    
def delete_sales(request):
    if request.method == 'POST':
        # Get the lead ID from the request data
        lead_id = request.POST.get('lead_id')

        try:
            # Try to fetch the lead from the database
            lead = Sales.objects.get(lead_id=lead_id)
            # Delete the lead
            lead.delete()
            # Return a success response
            return JsonResponse({'success': True})
        except Sales.DoesNotExist:
            # If the lead does not exist, return an error response
            return JsonResponse({'success': False, 'error': 'Sales does not exist'})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
def add_build(request):
    if request.method == 'POST':
        # Extract form data
        build_id = request.POST.get('build_id')
        strategist_name_id = request.POST.get('strategist_name')
        strategist_number = request.POST.get('strategist_number')
        email_id = request.POST.get('email_id')
        date = request.POST.get('date')
        strategy = request.POST.get('strategy')
        document = request.POST.get('document')
        payment_date = request.POST.get('payment_date')
        payment_amount = request.POST.get('payment_amount')
        delivery_date = request.POST.get('delivery_date')
        remarks = request.POST.get('remarks')
        status = request.POST.get('status')
        source = request.POST.get('source')
        assign_from = request.POST.get('assign_from')
        manage_by = request.POST.get('manage_by')

        # Validate and convert dates if needed
        # For example:
        # try:
        #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # except ValueError:
        #     return JsonResponse({'error': 'Invalid date format for date'}, status=400)

        # Check if the provided strategist_name_id exists
        if strategist_name_id:
            try:
                strategist_name = AlgobullsEmployee.objects.get(employee_id=strategist_name_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            strategist_name = None

        # Create a new Build object and save it to the database
        new_build = Build.objects.create(
            build_id=build_id,
            strategist_name=strategist_name,
            strategist_number=strategist_number,
            email_id=email_id,
            date=date,
            strategy=strategy,
            document=document,
            payment_date=payment_date,
            payment_amount=payment_amount,
            delivery_date=delivery_date,
            remarks=remarks,
            status=status,
            source=source,
            assign_from=assign_from,
            manage_by=manage_by,
        )

        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        sales_employees = AlgobullsEmployee.objects.all()
        

        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'sales_employees' : sales_employees,
            
        }

        return render(request, 'add_build.html', context)

def add_tech_task(request):
    if request.method == 'POST':
        # Extract form data
        task_id = request.POST.get('task_id')
        employee_id_id = request.POST.get('employee_id')
        date = request.POST.get('date')
        task = request.POST.get('task')
        nature = request.POST.get('nature')
        task_status = request.POST.get('task_status')
        priority = request.POST.get('priority')
        date_of_closing = request.POST.get('date_of_closing')
        number_of_days = request.POST.get('number_of_days')
        comments = request.POST.get('comments')

        # Validate and convert dates if needed
        # For example:
        # try:
        #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # except ValueError:
        #     return JsonResponse({'error': 'Invalid date format for date'}, status=400)

        # Check if the provided employee_id_id exists
        if employee_id_id:
            try:
                employee_id = AlgobullsEmployee.objects.get(employee_id=employee_id_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            employee_id = None

        # Create a new TechTask object and save it to the database
        new_tech_task = TechTask.objects.create(
            task_id=task_id,
            employee_id=employee_id,
            date=date,
            task=task,
            nature=nature,
            task_status=task_status,
            priority=priority,
            date_of_closing=date_of_closing,
            number_of_days=number_of_days,
            comments=comments,
        )

        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        sales_employees = AlgobullsEmployee.objects.all()

        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'sales_employees': sales_employees,
        }

        return render(request, 'add_tech_task.html', context)

def add_support(request):
    if request.method == 'POST':
        # Extract form data
        ticket_number = request.POST.get('ticket_number')
        branch_employee_id_id = request.POST.get('branch_employee_id')
        date = request.POST.get('date')
        broking_id = request.POST.get('broking_id')
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        email_id = request.POST.get('email_id')
        date_of_error = request.POST.get('date_of_error')
        strategy_code = request.POST.get('strategy_code')
        strategy_instrument = request.POST.get('strategy_instrument')
        customer_type = request.POST.get('customer_type')
        priority = request.POST.get('priority')
        issue = request.POST.get('issue')
        comment = request.POST.get('comment')
        support_employee_id_id = request.POST.get('support_employee_id')
        division_employee_id_id = request.POST.get('division_employee_id')
        status = request.POST.get('status')
        date_of_closing = request.POST.get('date_of_closing')

        # Validate and convert dates if needed
        # For example:
        # try:
        #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # except ValueError:
        #     return JsonResponse({'error': 'Invalid date format for date'}, status=400)

        # Check if the provided branch_employee_id_id exists
        if branch_employee_id_id:
            try:
                branch_employee_id = BranchEmployee.objects.get(branch_employee_id=branch_employee_id_id)
            except BranchEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            branch_employee_id = None

        # Check if the provided support_employee_id exists
        if support_employee_id_id:
            try:
                support_employee = AlgobullsEmployee.objects.get(employee_id=support_employee_id_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            support_employee = None

        # Check if the provided division_employee_id exists
        if division_employee_id_id:
            try:
                division_employee = AlgobullsEmployee.objects.get(employee_id=division_employee_id_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            division_employee = None

        # Create a new Support object and save it to the database
        new_support = Support.objects.create(
            ticket_number=ticket_number,
            branch_employee_id=branch_employee_id,
            date=date,
            broking_id=broking_id,
            name=name,
            contact_number=contact_number,
            email_id=email_id,
            date_of_error=date_of_error,
            strategy_code=strategy_code,
            strategy_instrument=strategy_instrument,
            customer_type=customer_type,
            priority=priority,
            issue=issue,
            comment=comment,
            support_employee=support_employee,
            division_employee=division_employee,
            status=status,
            date_of_closing=date_of_closing,
        )

        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        branch_employees = BranchEmployee.objects.all()
        sales_employees = AlgobullsEmployee.objects.all()
        
        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'branch_employees': branch_employees,
            'sales_employees' : sales_employees,
        }

        return render(request, 'add_support.html', context)

def add_strategies(request):
    if request.method == 'POST':
        # Extract form data
        strategy_id = request.POST.get('strategy_id')
        employee_id_id = request.POST.get('employee_id')
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        broking_house = request.POST.get('broking_house')
        client_id = request.POST.get('client_id')

        # Check if the provided employee_id exists
        if employee_id_id:
            try:
                employee_id = AlgobullsEmployee.objects.get(employee_id=employee_id_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            employee_id = None

        # Create a new Strategies object and save it to the database
        new_strategy = Strategies.objects.create(
            strategy_id=strategy_id,
            employee_id=employee_id,
            name=name,
            mobile_number=mobile_number,
            broking_house=broking_house,
            client_id=client_id,
        )

        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        sales_employees = AlgobullsEmployee.objects.all()
        
        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'sales_employees' : sales_employees,
        }

        return render(request, 'add_strategies.html', context)

def delete_strategy(request):
    if request.method == 'POST':
        # Get the strategy ID from the request data
        strategy_id = request.POST.get('strategy_id')

        try:
            # Try to fetch the strategy from the database
            strategy = Strategies.objects.get(strategy_id=strategy_id)
            # Delete the strategy
            strategy.delete()
            # Return a success response
            return JsonResponse({'success': True})
        except Strategies.DoesNotExist:
            # If the strategy does not exist, return an error response
            return JsonResponse({'success': False, 'error': 'Strategy does not exist'})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_support(request):
    if request.method == 'POST':
        # Get the ticket number from the request data
        ticket_number = request.POST.get('ticket_number')

        try:
            # Try to fetch the support from the database
            support = Support.objects.get(ticket_number=ticket_number)
            # Delete the support
            support.delete()
            # Return a success response
            return JsonResponse({'success': True})
        except Support.DoesNotExist:
            # If the support does not exist, return an error response
            return JsonResponse({'success': False, 'error': 'Support does not exist'})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_tech_task(request):
    if request.method == 'POST':
        # Get the task ID from the request data
        task_id = request.POST.get('task_id')

        try:
            # Try to fetch the tech task from the database
            task = TechTask.objects.get(task_id=task_id)
            # Delete the tech task
            task.delete()
            # Return a success response
            return JsonResponse({'success': True})
        except TechTask.DoesNotExist:
            # If the tech task does not exist, return an error response
            return JsonResponse({'success': False, 'error': 'Tech Task does not exist'})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_build(request):
    if request.method == 'POST':
        # Get the build ID from the request data
        build_id = request.POST.get('build_id')

        try:
            # Try to fetch the build from the database
            build = Build.objects.get(build_id=build_id)
            # Delete the build
            build.delete()
            # Return a success response
            return JsonResponse({'success': True})
        except Build.DoesNotExist:
            # If the build does not exist, return an error response
            return JsonResponse({'success': False, 'error': 'Build does not exist'})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def update_build(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for build_id, build_data in updated_data.items():
            try:
                build = Build.objects.get(build_id=build_id)
                for field, value in build_data.items():
                    setattr(build, field, value)
                build.save()
                success_count += 1
            except Build.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})

import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import TechTask  # Import your TechTask model

def update_tech_task(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for task_id, task_data in updated_data.items():
            try:
                task = TechTask.objects.get(task_id=task_id)
                for field, value in task_data.items():
                    setattr(task, field, value)
                task.save()
                success_count += 1
            except TechTask.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})

from django.http import JsonResponse
from .models import Support
import json

def update_support(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for ticket_number, support_data in updated_data.items():
            try:
                support = Support.objects.get(ticket_number=ticket_number)
                for field, value in support_data.items():
                    setattr(support, field, value)
                support.save()
                success_count += 1
            except Support.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})

def update_strategies(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for strategy_id, strategy_data in updated_data.items():
            try:
                strategy = Strategies.objects.get(strategy_id=strategy_id)
                for field, value in strategy_data.items():
                    setattr(strategy, field, value)
                strategy.save()
                success_count += 1
            except Strategies.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})
