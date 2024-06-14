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
from .models import AlgobullsEmployee, Sales, BranchEmployee, Build, TechTask, Support, Strategies, Rms, Broker
from datetime import datetime, date
from .models import Support, BranchEmployee, AlgobullsEmployee
from django.shortcuts import render, redirect

def to_login(request):
    return redirect("/accounts/login/")

# Create your views here.
@login_required
def home(request):
    # Fetch AlgobullsEmployee object corresponding to the currently logged-in user's email address
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
    
    sales_leads = Sales.objects.all().order_by('lead_id')
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    build = Build.objects.all().order_by('build_id')
    tech_task = TechTask.objects.all().order_by('task_id')
    support = Support.objects.all().order_by('ticket_number')
    strategies = Strategies.objects.all().order_by('strategy_id')
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
    #     name = branch_employee.name
    # else:
    #     name = algobulls_employee.name
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'builds' : build,
        'tech_tasks' : tech_task,
        'supports' : support,
        'strategies' : strategies,
        'selected_status': request.GET.get('status', '')
    }
    
    for permission in user_permissions:
        if (permission.name == "Can view Sales"):
            return redirect('/sales-leads/')
    for permission in user_permissions:
        if (permission.name == "Can view Build"):
            return redirect('/build/')
    for permission in user_permissions:
        if (permission.name == "Can view Tech Task"):
            return redirect('/tech_task/')
    for permission in user_permissions:
        if (permission.name == "Can view Support"):
            return redirect('/support/')
    for permission in user_permissions:
        if (permission.name == "Can view Strategies"):
            return redirect('/strategies/')
    for permission in user_permissions:
        if (permission.name == "Can view RMS"):
            return redirect('/rms/')

    return render(request, 'base.html', context)

import pyotp
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

def generate_totp_key():
    return "Prospace"

def get_totp(key):
    return pyotp.TOTP(key)

def generate_qr_code_base64(uri):
    qr = qrcode.make(uri)
    buffered = BytesIO()
    qr.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@login_required
def auth(request):
    print(request.session.get("email"))
    current_time = timezone.now()
    last_login_time_str = request.session.get('last_login_time')
    request.session.save()
    # Debugging: Print current and last login time
    print("Current time:", current_time)
    print("Last login time from session:", last_login_time_str)
    
    if last_login_time_str:
        last_login_time = datetime.fromisoformat(last_login_time_str)
        print("Parsed last login time:", last_login_time)
        
        if current_time - last_login_time < timedelta(minutes=1):
            request.session['authenticated'] = True
            request.session['last_login_time'] = current_time.isoformat()
            request.session.modified = True
            request.session.save()  # Explicitly save the session
            return redirect('/home/')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        key = generate_totp_key()
        totp = get_totp(key)
        
        print("Session keys before verifying OTP:", request.session.keys())

        if totp.verify(otp):
            request.session['authenticated'] = True
            email = request.user.username
            request.session["email"]=email
            
            request.session['last_login_time'] = current_time.isoformat()
            request.session.modified = True
            request.session.save()  # Explicitly save the session
            print("New last_login_time set:", request.session['last_login_time'])
            print("Session keys after setting last_login_time:", request.session.keys())
            return redirect('/home/')
        else:
            return render(request, 'auth.html', {'error': 'OTP Not Verified'})
    else:
        key = generate_totp_key()
        uri = get_totp(key).provisioning_uri(name="pspace", issuer_name="ahil")
        qr_base64 = generate_qr_code_base64(uri)
        context = {'qr': qr_base64}
        return render(request, 'auth.html', context)
   
from django.contrib.auth import logout as auth_logout
     
def custom_logout(request):
    # Retain session data before logout
    if 'authenticated' in request.session:
        auth_logout(request)
        # Optionally reset session data
        request.session['authenticated'] = False
        print("User logged out, session cleared.")  # Debug

    # Redirect to the login page after logout
    return redirect('/accounts/login/')

from django.shortcuts import render
from .models import Sales, Support, AlgobullsEmployee, BranchEmployee

def status_filter(request, table, status):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
    
    sales_leads = Sales.objects.filter(status=status).order_by('lead_id')
    number_of_sales_status = sales_leads.count()
    
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    
    build = Build.objects.all().order_by('build_id')
    
    tech_task = TechTask.objects.filter(task_status=status).order_by('task_id')
    number_of_tech_task_status = tech_task.count()
    
    support = Support.objects.filter(status=status).order_by('ticket_number')
    number_of_support_status = support.count()
    
    strategies = Strategies.objects.all().order_by('strategy_id')
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
        number_of_sales_status = sales_leads.count()
        number_of_support_status = support.count()
        
    if user_group == "Branch Head":
        head_branch_id = branch_employee.branch_id
        sales_leads = sales_leads.filter(branch_employee_id__branch_id=head_branch_id)
        support = support.filter(branch_employee_id__branch_id=head_branch_id)
        number_of_sales_status = sales_leads.count()
        number_of_support_status = support.count()
        
    if user_group == "Sales Employee":
        sales_leads = sales_leads.filter(sales_employee_id=employee_id)
        number_of_sales_status = sales_leads.count()
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'builds' : build,
        'tech_tasks' : tech_task,
        'supports' : support,
        'strategies' : strategies,
        'selected_status': status,
        'table':table,
        'number_of_sales_status':number_of_sales_status,
        'number_of_support_status':number_of_support_status,
        'number_of_tech_task_status':number_of_tech_task_status,
    }
    if table=="sales-leads":
        return render(request, 'sales.html', context)
    
    if table=="support":
        return render(request, 'support.html', context)
    
    if table=="build":
        return render(request, "build.html", context)
    
    if table=="strategies":
        return render(request, "strategies.html", context)
    
    if table=='tech-task':
        return render(request, 'tech_task.html', context)
    
    
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
                            branch_employee_id = BranchEmployee.objects.get(employee_id=value)
                            setattr(lead, field, branch_employee_id)
                        except BranchEmployee.DoesNotExist:
                            # Handle the case where the provided branch employee ID does not exist
                            error_count += 1
                            continue  # Skip to the next iteration
                    elif field == 'sales_employee_id':
                        # Handle sales employee ID separately
                        try:
                            sales_employee_id = AlgobullsEmployee.objects.get(employee_id=value)
                            setattr(lead, field, sales_employee_id)
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

from django.db.models import Max
from django.db.models import IntegerField
from django.db.models.functions import Cast

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
        entry_date= request.POST.get('entry_date')
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
            entry_date=entry_date,
            status=status,
            reason_for_dropped=reason_for_dropped,
        )

        # Fetch Algobulls employee and user information
        
        return redirect('/sales-leads/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        branch_employees = BranchEmployee.objects.all()
        sales_employees = AlgobullsEmployee.objects.all()
        today_date = date.today()
        
        # max_lead_id = Sales.objects.aggregate(max_lead_id=Max('lead_id'))['max_lead_id']
        # max_lead_id = int(max_lead_id)
        # new_lead_id = max_lead_id + 1
        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())
            
        # last_lead = Sales.objects.order_by('lead_id').last()
        # print(last_lead.lead_id)

        context = {
            'user_permissions': user_permissions,
            'branch_employees': branch_employees,
            'sales_employees' : sales_employees,
            'today_date': today_date,
            # 'new_lead_id': new_lead_id,
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

        return redirect('/build/')

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

        return redirect('/tech_task/')

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
        division_assigned_to = request.POST.get('division_assigned_to')

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
            division_assigned_to=division_assigned_to,
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
    
def delete_rms(request):
    if request.method == 'POST':
        sr_no = request.POST.get('sr_no')

        try:
            # Fetch the RMS entry from the database using sr_no
            rms = Rms.objects.get(sr_no=sr_no)
            # Delete the RMS entry
            rms.delete()
            return JsonResponse({'success': True})
        except Rms.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'RMS does not exist'})
    else:
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
                    # Special handling for strategist_name.employee_id field
                    if field == 'strategist_name':
                        # Assuming you have a ForeignKey field strategist_name in Build model
                        employee_id = int(value)
                        try:
                            # Get the AlgobullsEmployee instance based on the employee_id
                            strategist = AlgobullsEmployee.objects.get(employee_id=employee_id)
                            # Assign the AlgobullsEmployee instance to the strategist_name field of the Build instance
                            build.strategist_name = strategist
                        except AlgobullsEmployee.DoesNotExist:
                            # Handle the case where the AlgobullsEmployee with the provided ID does not exist
                            error_count += 1
                            continue
                    else:
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
                    # Convert employee_id to integer if the field is employee_id
                    if field == 'employee_id':
                        value = AlgobullsEmployee.objects.get(employee_id=value)
                    setattr(task, field, value)
                task.save()
                success_count += 1
            except TechTask.DoesNotExist:
                error_count += 1
            except AlgobullsEmployee.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})
      
    else:
        return JsonResponse({'error': 'Invalid request method'})

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
                    if field in ['support_employee', 'division_employee']:
                        # Check if value is a valid employee_id and get the AlgobullsEmployee object
                        try:
                            employee = AlgobullsEmployee.objects.get(employee_id=value)
                            setattr(support, field, employee)
                        except AlgobullsEmployee.DoesNotExist:
                            error_count += 1
                            continue  # Skip to the next field if employee is not found
                    else:
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
                    if field == 'employee_id':
                        try:
                            employee = AlgobullsEmployee.objects.get(employee_id=value)
                            setattr(strategy, field, employee)
                        except AlgobullsEmployee.DoesNotExist:
                            error_count += 1
                            continue  # Skip to the next field if employee is not found
                    else:
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

def update_rms(request):
    if request.method == 'POST':
        updated_data_json = request.POST.get('updated_data')
        updated_data = json.loads(updated_data_json)

        success_count = 0
        error_count = 0

        # Update records in the database based on the received data
        for sr_no, rms_data in updated_data.items():
            try:
                rms = Rms.objects.get(sr_no=sr_no)
                for field, value in rms_data.items():
                    if field == 'broker':
                        # Check if value is a valid broker_id and get the Broker object
                        try:
                            broker = Broker.objects.get(broker_id=value)
                            setattr(rms, field, broker)
                        except Broker.DoesNotExist:
                            error_count += 1
                            continue
                    elif field == 'employee':
                        # Check if value is a valid employee_id and get the AlgobullsEmployee object
                        try:
                            employee = AlgobullsEmployee.objects.get(employee_id=value)
                            setattr(rms, field, employee)
                        except AlgobullsEmployee.DoesNotExist:
                            error_count += 1
                            continue
                    else:
                        setattr(rms, field, value)
                rms.save()
                success_count += 1
            except Rms.DoesNotExist:
                error_count += 1

        success_message = f"{success_count} records updated successfully."
        error_message = f"{error_count} records failed to update."

        return JsonResponse({'success_message': success_message, 'error_message': error_message})

    else:
        return JsonResponse({'error': 'Invalid request method'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Sales # Adjust the import according to your models

@csrf_exempt
@require_POST
def update_sales(request):
    try:
        data = json.loads(request.POST.get('updated_data'))
        for lead_id, fields in data.items():
            try:
                lead = Sales.objects.get(id=lead_id)
                for field, value in fields.items():
                    setattr(lead, field, value)
                lead.save()
            except Sales.DoesNotExist:
                return JsonResponse({'error': f'SalesLead with id {lead_id} does not exist'}, status=400)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.http import JsonResponse
from .models import AlgobullsEmployee, AlgobullsDivision
from django.shortcuts import get_object_or_404

def get_division_employees(request):
    division_name = request.GET.get('division')
    if division_name:
        # Ensure proper sanitization of division name
        division_name = division_name.strip()

        # Retrieve the division object using the provided division name or return a 404 error if not found
        division = get_object_or_404(AlgobullsDivision, division_name=division_name)

        # Filter employees based on the retrieved division object
        employees = AlgobullsEmployee.objects.filter(division_name=division)

        # Prepare the employee data to send in the JSON response
        employee_list = [
            {'employee_id': employee.employee_id, 'name': employee.name} for employee in employees
        ]

        # Return the employee data as a JSON response
        return JsonResponse({'employees': employee_list})
    else:
        # Return an error response if the division is not specified
        return JsonResponse({'error': 'Division not specified'}, status=400)

from django.http import JsonResponse
from .models import Sales, Support

def get_status_values(request, table):
    # if request.is_ajax():
        if table == 'sales-leads':
            status_values = Sales.objects.values_list('status', flat=True).distinct()
        elif table == 'support':
            status_values = Support.objects.values_list('status', flat=True).distinct()
        else:
            status_values = []
        return JsonResponse({'status_values': list(status_values)})
    
def sales(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
    
    sales_leads = Sales.objects.all().order_by('lead_id')
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    build = Build.objects.all().order_by('build_id')
    tech_task = TechTask.objects.all().order_by('task_id')
    support = Support.objects.all().order_by('ticket_number')
    strategies = Strategies.objects.all().order_by('strategy_id')
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    sales_leads = Sales.objects.select_related('sales_employee_id').all()
    unique_sales_employees = set()
    for lead in sales_leads:
        if lead.sales_employee_id:
            unique_sales_employees.add((lead.sales_employee_id.employee_id, lead.sales_employee_id.name))
    
    sales_leads = Sales.objects.select_related('branch_employee_id__branch_id__broker_id').all()
    unique_branch_ids = set()
    unique_broker_names = set()
    for lead in sales_leads:
        if lead.branch_employee_id and lead.branch_employee_id.branch_id:
            unique_branch_ids.add((lead.branch_employee_id.branch_id.branch_id, lead.branch_employee_id.branch_id.branch_id))
            if lead.branch_employee_id.branch_id.broker_id:
                unique_broker_names.add((lead.branch_employee_id.branch_id.broker_id.broker_id, lead.branch_employee_id.branch_id.broker_id.broker_name))
            
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
        
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        sales_leads = Sales.objects.filter(entry_date__range=[start_date, end_date]).order_by('lead_id')

    # sales_leads = Sales.objects.all().order_by('lead_id')
    sales_leads = Sales.objects.annotate(
            lead_id_as_int=Cast('lead_id', IntegerField())
        ).order_by('lead_id_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'builds' : build,
        'tech_tasks' : tech_task,
        'supports' : support,
        'strategies' : strategies,
        'selected_status': request.GET.get('status', ''),
        'unique_sales_employees': unique_sales_employees,
        'unique_branch_ids': unique_branch_ids,
        'unique_broker_names': unique_broker_names,
    }
    
    return render(request, 'sales.html', context)

def support(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
    
    supports = Support.objects.select_related('support_employee').all()
    unique_support_employees = set()
    for support in supports:
        if support.support_employee:
            unique_support_employees.add((support.support_employee.employee_id, support.support_employee.name))
    
    supports = Support.objects.select_related('division_employee').all()
    unique_division_employees = set()
    for support in supports:
        if support.division_employee:
            unique_division_employees.add((support.division_employee.employee_id, support.division_employee.name))
    
    supports = Support.objects.select_related('branch_employee_id__branch_id__broker_id').all()
    unique_branch_ids = set()
    unique_broker_names = set()
    for support in supports:
        if support.branch_employee_id and support.branch_employee_id.branch_id:
            unique_branch_ids.add((support.branch_employee_id.branch_id.branch_id, support.branch_employee_id.branch_id.branch_id))
            if support.branch_employee_id.branch_id.broker_id:
                unique_broker_names.add((support.branch_employee_id.branch_id.broker_id.broker_id, support.branch_employee_id.branch_id.broker_id.broker_name))
    
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
        
    support = Support.objects.annotate(
            ticket_number_as_int=Cast('ticket_number', IntegerField())
        ).order_by('ticket_number_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'supports' : support,
        'selected_status': request.GET.get('status', ''),
        'unique_support_employees':unique_support_employees,
        'unique_division_employees':unique_division_employees,
        'unique_branch_ids': unique_branch_ids,
        'unique_broker_names': unique_broker_names,
    }
    
    return render(request, 'support.html', context)        


def build(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
        
    builds = Build.objects.select_related('strategist_name').all()
    unique_strategist_names = set()
    for build in builds:
        if build.strategist_name:
            unique_strategist_names.add((build.strategist_name.employee_id, build.strategist_name.name))

    
    sales_leads = Sales.objects.all().order_by('lead_id')
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
        
    build = Build.objects.annotate(
            build_id_as_int=Cast('build_id', IntegerField())
        ).order_by('build_id_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'builds' : build,
        'selected_status': request.GET.get('status', ''),
        'unique_strategist_names': unique_strategist_names,
    }
    
    return render(request, 'build.html', context) 


def strategies(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
        
    strategies = Strategies.objects.select_related('employee_id').all()
    unique_employee_ids = set()
    for strategy in strategies:
        if strategy.employee_id:
            unique_employee_ids.add((strategy.employee_id.employee_id, strategy.employee_id.name))
    
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
        
    strategies = Strategies.objects.annotate(
            strategy_id_as_int=Cast('strategy_id', IntegerField())
        ).order_by('strategy_id_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'strategies' : strategies,
        'selected_status': request.GET.get('status', ''),
        'unique_employee_ids': unique_employee_ids,
    }
    
    return render(request, 'strategies.html', context)        


def tech_task(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
        
    tech_tasks = TechTask.objects.select_related('employee_id').all()
    unique_employee_ids = set()
    for tech_task in tech_tasks:
        if tech_task.employee_id:
            unique_employee_ids.add((tech_task.employee_id.employee_id, tech_task.employee_id.name))

    
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    tech_task = TechTask.objects.all().order_by('task_id')
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
    
    tech_task = TechTask.objects.annotate(
            task_id_as_int=Cast('task_id', IntegerField())
        ).order_by('task_id_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'tech_tasks' : tech_task,
        'selected_status': request.GET.get('status', ''),
        'unique_employee_ids': unique_employee_ids,
    }
    
    return render(request, 'tech_task.html', context)        

def rms(request):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
        
    rmss = Rms.objects.select_related('employee').all()
    unique_employees = set()
    for rms in rmss:
        if rms.employee:
            unique_employees.add((rms.employee.employee_id, rms.employee.name))
    
    rmss = Rms.objects.select_related('broker').all()
    unique_brokers = set()
    for rms in rmss:
        if rms.broker.broker_id:
            unique_brokers.add((rms.broker.broker_id, rms.broker.broker_name))

    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    rms = Rms.objects.all().order_by('sr_no')
    broker = Broker.objects.all()
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        support = support.filter(branch_employee_id=employee_id)
    
    rms = Rms.objects.annotate(
            sr_no_as_int=Cast('sr_no', IntegerField())
        ).order_by('sr_no_as_int')
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'rms_objects': rms,
        'brokers': broker,
        'selected_status': request.GET.get('status', ''),
        'unique_employees': unique_employees,
        'unique_brokers': unique_brokers,
    }
    
    return render(request, 'rms.html', context)        

def add_rms(request):
    if request.method == 'POST':
        # Extract form data
        sr_no = request.POST.get('sr_no')
        ticket_number = request.POST.get('ticket_number')
        broker_id = request.POST.get('broker')
        date = request.POST.get('date')
        broking_id = request.POST.get('broking_id')
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        email_id = request.POST.get('email_id')
        customer_type = request.POST.get('customer_type')
        priority = request.POST.get('priority')
        issue = request.POST.get('issue')
        comment = request.POST.get('comment')
        assigned_to = request.POST.get('assigned_to')
        status = request.POST.get('status')
        date_of_closing = request.POST.get('date_of_closing')
        rms_status = request.POST.get('rms_status')
        rms_comment = request.POST.get('rms_comment')
        employee_id = request.POST.get('employee')

        # Validate and convert dates if needed
        # For example:
        # try:
        #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # except ValueError:
        #     return JsonResponse({'error': 'Invalid date format for date'}, status=400)

        # Check if the provided broker_id exists
        if broker_id:
            try:
                broker = Broker.objects.get(broker_id=broker_id)
            except Broker.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            broker = None

        # Check if the provided employee_id exists
        if employee_id:
            try:
                employee = AlgobullsEmployee.objects.get(employee_id=employee_id)
            except AlgobullsEmployee.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page or handle the error appropriately
        else:
            employee = None

        # Create a new Rms object and save it to the database
        new_rms = Rms.objects.create(
            sr_no=sr_no,
            ticket_number=ticket_number,
            broker=broker,
            date=date,
            broking_id=broking_id,
            name=name,
            contact_number=contact_number,
            email_id=email_id,
            customer_type=customer_type,
            priority=priority,
            issue=issue,
            comment=comment,
            assigned_to=assigned_to,
            status=status,
            date_of_closing=date_of_closing,
            rms_status=rms_status,
            rms_comment=rms_comment,
            employee=employee,
        )

        return redirect('/accounts/profile/')

    else:
        # Fetch user groups
        user_groups = request.user.groups.all()
        brokers = Broker.objects.all()
        employees = AlgobullsEmployee.objects.all()
        
        # Fetch user permissions
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())

        context = {
            'user_permissions': user_permissions,
            'brokers': brokers,
            'sales_employees': employees,
        }

        return render(request, 'add_rms.html', context)

from django.shortcuts import render
from datetime import datetime, timedelta

def to_sales_analysis(request):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    # sales_leads = Sales.objects.select_related('sales_employee_id').all()
    # unique_sales_employees = set()
    # for lead in sales_leads:
    #     if lead.sales_employee_id:
    #         unique_sales_employees.add((lead.sales_employee_id.employee_id, lead.sales_employee_id.name))
    
    # sales_leads = Sales.objects.select_related('branch_employee_id__branch_id__broker_id').all()
    # unique_branch_ids = set()
    # unique_broker_names = set()
    # for lead in sales_leads:
    #     if lead.branch_employee_id and lead.branch_employee_id.branch_id:
    #         unique_branch_ids.add((lead.branch_employee_id.branch_id.branch_id, lead.branch_employee_id.branch_id.branch_id))
    #         if lead.branch_employee_id.branch_id.broker_id:
    #             unique_broker_names.add((lead.branch_employee_id.branch_id.broker_id.broker_id, lead.branch_employee_id.branch_id.broker_id.broker_name))
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        # 'unique_sales_employees': unique_sales_employees,
        # 'unique_branch_ids': unique_branch_ids,
        # 'unique_broker_names': unique_broker_names,
    }
    
    return render(request, 'sales_analysis.html', context)

def to_support_analysis(request):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    supports = Support.objects.select_related('support_employee').all()
    unique_support_employees = set()
    for support in supports:
        if support.support_employee:
            unique_support_employees.add((support.support_employee.employee_id, support.support_employee.name))
    
    supports = Support.objects.select_related('division_employee').all()
    unique_division_employees = set()
    for support in supports:
        if support.division_employee:
            unique_division_employees.add((support.division_employee.employee_id, support.division_employee.name))
    
    supports = Support.objects.select_related('branch_employee_id__branch_id__broker_id').all()
    unique_branch_ids = set()
    unique_broker_names = set()
    for support in supports:
        if support.branch_employee_id and support.branch_employee_id.branch_id:
            unique_branch_ids.add((support.branch_employee_id.branch_id.branch_id, support.branch_employee_id.branch_id.branch_id))
            if support.branch_employee_id.branch_id.broker_id:
                unique_broker_names.add((support.branch_employee_id.branch_id.broker_id.broker_id, support.branch_employee_id.branch_id.broker_id.broker_name))
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'unique_support_employees':unique_support_employees,
        'unique_division_employees':unique_division_employees,
        'unique_branch_ids': unique_branch_ids,
        'unique_broker_names': unique_broker_names,
    }
    
    return render(request, 'support_analysis.html', context)

def to_rms_analysis(request):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    return render(request, 'rms_analysis.html', context)

def to_tech_task_analysis(request):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    return render(request, 'tech_task_analysis.html', context)

def to_build_analysis(request):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    builds = Build.objects.select_related('strategist_name').all()
    unique_strategist_names = set()
    for build in builds:
        if build.strategist_name:
            unique_strategist_names.add((build.strategist_name.employee_id, build.strategist_name.name))
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'), 
        'unique_strategist_names': unique_strategist_names,
    }
    
    return render(request, 'build_analysis.html', context)

from django.db import connection

def execute_raw_sql(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

import json
from django.http import JsonResponse
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

def sales_analysis_data(request):
    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        filters = json.loads(request.POST.get('filters', '{}'))

        source_types = filters.get('source_type', [])
        categories = filters.get('category', [])
        risk_appetites = filters.get('risk_appetite', [])
        statuses = filters.get('status', [])
        employee_ids = filters.get('employee_id', [])

        filter_conditions = []
        params = [start_date, end_date]

        def handle_empty_string(value):
            return None if value == '' else value

        if source_types:
            filter_conditions.append('"Source Type" IN %s')
            params.append(tuple(handle_empty_string(x) for x in source_types if x))
        if categories:
            filter_conditions.append('"Category" IN %s')
            params.append(tuple(handle_empty_string(x) for x in categories if x))
        if risk_appetites:
            filter_conditions.append('"Risk Appetite" IN %s')
            params.append(tuple(handle_empty_string(x) for x in risk_appetites if x))
        if statuses:
            filter_conditions.append('"Status" IN %s')
            params.append(tuple(handle_empty_string(x) for x in statuses if x))
        if employee_ids:
            filter_conditions.append('"Sales Employee ID" IN %s')
            params.append(tuple(handle_empty_string(x) for x in employee_ids if x))

        filter_sql = ' AND '.join(filter_conditions)

        query1 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Purchase Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Purchase Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Status",
                COUNT(*) AS total_leads
            FROM "Sales"
            WHERE "Purchase Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY week_start, week_end, "Status"
            ORDER BY week_start, "Status";
        """
        query2 = f"""
            SELECT
                "Branch Employee ID",
                COUNT(*) AS total_leads,
                SUM(CASE WHEN "Status" = 'Converted' THEN 1 ELSE 0 END) AS Converted,
                SUM(CASE WHEN "Status" = 'Dropped' THEN 1 ELSE 0 END) AS Dropped,
                SUM(CASE WHEN "Status" = 'Follow up' THEN 1 ELSE 0 END) AS "Follow up",
                SUM(CASE WHEN "Status" = 'No Answer' THEN 1 ELSE 0 END) AS "No Answer",
                SUM(CASE WHEN "Status" = 'Not Interested' THEN 1 ELSE 0 END) AS "Not Interested",
                SUM(CASE WHEN "Status" = 'In Progress' THEN 1 ELSE 0 END) AS "In Progress"
            FROM "Sales"
            WHERE "Purchase Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY "Branch Employee ID"
            ORDER BY "Branch Employee ID";
        """
        query3 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Purchase Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Purchase Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                SUM(CAST(NULLIF("Amount", '') AS DECIMAL)) AS total_revenue
            FROM "Sales"
            WHERE "Purchase Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY week_start, week_end
            ORDER BY week_start;
        """
        query4 = f"""
            SELECT
                "Branch Employee ID",
                SUM(CAST(NULLIF("Amount", '') AS DECIMAL)) AS branch_revenue
            FROM "Sales"
            WHERE "Purchase Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY "Branch Employee ID"
            ORDER BY "Branch Employee ID";
        """

        logger.info("Executing query1 with params: %s", params)
        results1 = execute_raw_sql(query1, params)
        logger.info("Executing query2 with params: %s", params)
        results2 = execute_raw_sql(query2, params)
        logger.info("Executing query3 with params: %s", params)
        results3 = execute_raw_sql(query3, params)
        logger.info("Executing query4 with params: %s", params)
        results4 = execute_raw_sql(query4, params)

        user_groups = request.user.groups.all()
        user_permissions = []
        for group in user_groups:
            user_permissions.extend(group.permissions.all())
            
        weekly_data = {}
        statuses = ['Converted', 'Dropped', 'Follow up', 'No Answer', 'Not Interested', 'In Progress']

        for row in results1:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            status = row[2]
            total_leads = row[3]
            
            week_label = f'{week_start} - {week_end}'

            if week_label not in weekly_data:
                weekly_data[week_label] = {status: 0 for status in statuses}
            
            weekly_data[week_label][status] += total_leads
            
        response1 = {
            'labels': list(weekly_data.keys()),
            'datasets': [
                {
                    'name': status,
                    'data': [weekly_data[week].get(status, 0) for week in weekly_data]
                } for status in statuses
            ]
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'results1': response1,
                'results2': results2,
                'results3': results3,
                'results4': results4,
            }
            return JsonResponse(data)
        else:
            context = {
                'start_date': start_date,
                'end_date': end_date,
                'results1': results1,
                'results2': results2,
                'results3': results3,
                'results4': results4,
            }
            return render(request, 'sales_analysis.html', context)
    except Exception as e:
        logger.error("Error in sales_analysis_data view: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def support_analysis_data(request):
    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Query for weekly data
        query1 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Status",
                COUNT(*) AS total_leads
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Status"
            ORDER BY week_start, "Status";
        """
        results1 = execute_raw_sql(query1, [start_date, end_date])
        
        # Query for status-wise data
        query2 = f"""
            SELECT
                "Status",
                COUNT(*) AS count
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Status"
            ORDER BY "Status";
        """
        results2 = execute_raw_sql(query2, [start_date, end_date])
        
        # Query for weekly priority data
        query3 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Priority",
                COUNT(*) AS total_leads
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Priority"
            ORDER BY week_start, "Priority";
        """
        results3 = execute_raw_sql(query3, [start_date, end_date])
        
        # Query for priority-wise data
        query4 = f"""
            SELECT
                "Priority",
                COUNT(*) AS count
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Priority"
            ORDER BY "Priority";
        """
        results4 = execute_raw_sql(query4, [start_date, end_date])
        
        # Query for weekly division data
        query5 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Division Assigned To",
                COUNT(*) AS total_leads
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Division Assigned To"
            ORDER BY week_start, "Division Assigned To";
        """
        results5 = execute_raw_sql(query5, [start_date, end_date])
        
        # Query for division-wise data
        query6 = f"""
            SELECT
                "Division Assigned To",
                COUNT(*) AS count
            FROM "Support"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Division Assigned To"
            ORDER BY "Division Assigned To";
        """
        results6 = execute_raw_sql(query6, [start_date, end_date])
        
        # Prepare data for weekly status chart
        weekly_data = OrderedDict()
        statuses = ['Open', 'In Progress', 'Hold', 'Resolved']

        for row in results1:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            status = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in weekly_data:
                weekly_data[week_label] = {status: 0 for status in statuses}
            
            weekly_data[week_label][status] += total_leads
            
        response1 = {
            'labels': list(weekly_data.keys()),
            'datasets': [
                {
                    'label': status,
                    'data': [weekly_data[week].get(status, 0) for week in weekly_data],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                } for status in statuses
            ]
        }
        
        # Prepare data for status pie chart
        status_data = {row[0]: row[1] for row in results2}
        
        response2 = {
            'labels': list(status_data.keys()),
            'datasets': [{
                'data': list(status_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Prepare data for weekly priority chart
        priority_weekly_data = OrderedDict()
        priorities = ['High', 'Medium', 'Low']

        for row in results3:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            priority = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in priority_weekly_data:
                priority_weekly_data[week_label] = {priority: 0 for priority in priorities}
            
            priority_weekly_data[week_label][priority] += total_leads
            
        response3 = {
            'labels': list(priority_weekly_data.keys()),
            'datasets': [
                {
                    'label': priority,
                    'data': [priority_weekly_data[week].get(priority, 0) for week in priority_weekly_data],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                } for priority in priorities
            ]
        }

        # Prepare data for priority pie chart
        priority_data = {row[0]: row[1] for row in results4}
        
        response4 = {
            'labels': list(priority_data.keys()),
            'datasets': [{
                'data': list(priority_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Prepare data for weekly division chart
        division_weekly_data = OrderedDict()
        divisions = ['Tech', 'Build', 'RMS', 'Sales', 'Strategy', 'Support']

        for row in results5:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            division = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in division_weekly_data:
                division_weekly_data[week_label] = {division: 0 for division in divisions}
            
            division_weekly_data[week_label][division] += total_leads
            
        response5 = {
            'labels': list(division_weekly_data.keys()),
            'datasets': [
                {
                    'label': division,
                    'data': [division_weekly_data[week].get(division, 0) for week in division_weekly_data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                } for division in divisions
            ]
        }

        # Prepare data for division pie chart
        division_data = {row[0]: row[1] for row in results6}
        
        response6 = {
            'labels': list(division_data.keys()),
            'datasets': [{
                'data': list(division_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
                'results5': response5,
                'results6': response6,
            }
            return JsonResponse(data)
        else:
            context = {
                'start_date': start_date,
                'end_date': end_date,
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
                'results5': response5,
                'results6': response6,
            }
            return render(request, 'support_analysis.html', context)
    except Exception as e:
        logger.error("Error in support_analysis_data view: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def rms_analysis_data(request):
    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Query for weekly data
        query1 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Status",
                COUNT(*) AS total_leads
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Status"
            ORDER BY week_start, "Status";
        """
        results1 = execute_raw_sql(query1, [start_date, end_date])
        
        # Query for status-wise data
        query2 = f"""
            SELECT
                "Status",
                COUNT(*) AS count
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Status"
            ORDER BY "Status";
        """
        results2 = execute_raw_sql(query2, [start_date, end_date])
        
        # Query for weekly priority data
        query3 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Issue",
                COUNT(*) AS total_leads
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Issue"
            ORDER BY week_start, "Issue";
        """
        results3 = execute_raw_sql(query3, [start_date, end_date])
        
        # Query for priority-wise data
        query4 = f"""
            SELECT
                "Issue",
                COUNT(*) AS count
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Issue"
            ORDER BY "Issue";
        """
        results4 = execute_raw_sql(query4, [start_date, end_date])
        
        # Query for weekly division data
        query5 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Customer Type",
                COUNT(*) AS total_leads
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Customer Type"
            ORDER BY week_start, "Customer Type";
        """
        results5 = execute_raw_sql(query5, [start_date, end_date])
        
        # Query for division-wise data
        query6 = f"""
            SELECT
                "Customer Type",
                COUNT(*) AS count
            FROM "Rms"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Customer Type"
            ORDER BY "Customer Type";
        """
        results6 = execute_raw_sql(query6, [start_date, end_date])
        
        # Prepare data for weekly status chart
        weekly_data = {}
        statuses = ['Open', 'In Progress', 'Hold', 'Resolved']

        for row in results1:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            status = row[2]
            total_leads = row[3]

            if week_start not in weekly_data:
                weekly_data[week_start] = {status: 0 for status in statuses}

            weekly_data[week_start][status] += total_leads

        response1 = {
            'labels': [f"{week_start} to {weekly_data[week_start].get('week_end', '')}" for week_start in weekly_data.keys()],
            'datasets': [
                {
                    'name': status,
                    'data': [weekly_data[week].get(status, 0) for week in weekly_data],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                } for status in statuses
            ]
        }

        
        # Prepare data for status pie chart
        status_data = {row[0]: row[1] for row in results2}
        
        response2 = {
            'labels': list(status_data.keys()),
            'datasets': [{
                'data': list(status_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Prepare data for weekly priority chart
        issue_weekly_data = {}
        issues = ['Strategy Development', 'Live Trading and RMS', 'Package and Funds', 'Front End Issues', 'General Info', 'Sales Related', 'Others']

        for row in results3:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = (row[0] + timedelta(days=6)).strftime('%Y-%m-%d')
            issue = row[2]
            total_leads = row[3]

            if week_start not in issue_weekly_data:
                issue_weekly_data[week_start] = {issue: 0 for issue in issues}
            
            issue_weekly_data[week_start][issue] += total_leads

        response3 = {
            'labels': [f"{week_start} to {week_end}" for week_start in issue_weekly_data.keys()],
            'datasets': [
                {
                    'name': issue,
                    'data': [issue_weekly_data[week].get(issue, 0) for week in issue_weekly_data],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                } for issue in issues
            ]
        }


        # Prepare data for priority pie chart
        issue_data = {row[0]: row[1] for row in results4}
        
        response4 = {
            'labels': list(issue_data.keys()),
            'datasets': [{
                'data': list(issue_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Prepare data for weekly division chart
        customer_type_weekly_data = {}
        customer_types = ['Choose', 'Build', 'Others']

        for row in results5:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = (row[0] + timedelta(days=6)).strftime('%Y-%m-%d')
            customer_type = row[2]
            total_leads = row[3]

            if week_start not in customer_type_weekly_data:
                customer_type_weekly_data[week_start] = {customer_type: 0 for customer_type in customer_types}
            
            customer_type_weekly_data[week_start][customer_type] += total_leads

        response5 = {
            'labels': [f"{week_start} to {week_end}" for week_start in customer_type_weekly_data.keys()],
            'datasets': [
                {
                    'name': customer_type,
                    'data': [customer_type_weekly_data[week].get(customer_type, 0) for week in customer_type_weekly_data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                } for customer_type in customer_types
            ]
        }


        # Prepare data for division pie chart
        customer_type_data = {row[0]: row[1] for row in results6}
        
        response6 = {
            'labels': list(customer_type_data.keys()),
            'datasets': [{
                'data': list(customer_type_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
                'results5': response5,
                'results6': response6,
            }
            return JsonResponse(data)
        else:
            context = {
                'start_date': start_date,
                'end_date': end_date,
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
                'results5': response5,
                'results6': response6,
            }
            return render(request, 'rms_analysis.html', context)
    except Exception as e:
        logger.error("Error in rms_analysis_data view: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

from collections import OrderedDict

def tech_task_analysis_data(request):
    try:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Query for weekly data
        query1 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Task Status",
                COUNT(*) AS total_leads
            FROM "Tech Task"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Task Status"
            ORDER BY week_start, "Task Status";
        """
        results1 = execute_raw_sql(query1, [start_date, end_date])
        
        # Query for status-wise data
        query2 = f"""
            SELECT
                "Task Status",
                COUNT(*) AS count
            FROM "Tech Task"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Task Status"
            ORDER BY "Task Status";
        """
        results2 = execute_raw_sql(query2, [start_date, end_date])
        
        # Query for weekly priority data
        query3 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Nature",
                COUNT(*) AS total_leads
            FROM "Tech Task"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY week_start, week_end, "Nature"
            ORDER BY week_start, "Nature";
        """
        results3 = execute_raw_sql(query3, [start_date, end_date])
        
        # Query for priority-wise data
        query4 = f"""
            SELECT
                "Nature",
                COUNT(*) AS count
            FROM "Tech Task"
            WHERE "Date" BETWEEN %s AND %s
            GROUP BY "Nature"
            ORDER BY "Nature";
        """
        results4 = execute_raw_sql(query4, [start_date, end_date])
        
        # Prepare data for weekly status chart
        weekly_data = OrderedDict()
        task_statuses = ['Pending Development', 'Under Development', 'Under Testing', 'Bugs Reported', 'Delivered or Closed', 'In Progress', 'On Hold', 'Open']

        for row in results1:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            task_status = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in weekly_data:
                weekly_data[week_label] = {task_status: 0 for task_status in task_statuses}
            
            weekly_data[week_label][task_status] += total_leads
            
        response1 = {
            'labels': list(weekly_data.keys()),
            'datasets': [
                {
                    'label': task_status,
                    'data': [weekly_data[week].get(task_status, 0) for week in weekly_data],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                } for task_status in task_statuses
            ]
        }
        
        # Prepare data for status pie chart
        task_status_data = {row[0]: row[1] for row in results2}
        
        response2 = {
            'labels': list(task_status_data.keys()),
            'datasets': [{
                'data': list(task_status_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Prepare data for weekly priority chart
        nature_weekly_data = OrderedDict()
        natures = ['Core Change', 'Strategy Change', 'None Core Request', 'Broker Integration', 'Operations']

        for row in results3:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            nature = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in nature_weekly_data:
                nature_weekly_data[week_label] = {nature: 0 for nature in natures}
            
            nature_weekly_data[week_label][nature] += total_leads
            
        response3 = {
            'labels': list(nature_weekly_data.keys()),
            'datasets': [
                {
                    'label': nature,
                    'data': [nature_weekly_data[week].get(nature, 0) for week in nature_weekly_data],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                } for nature in natures
            ]
        }

        # Prepare data for priority pie chart
        nature_data = {row[0]: row[1] for row in results4}
        
        response4 = {
            'labels': list(nature_data.keys()),
            'datasets': [{
                'data': list(nature_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                'borderWidth': 1
            }]
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
            }
            return JsonResponse(data)
        else:
            context = {
                'start_date': start_date,
                'end_date': end_date,
                'results1': response1,
                'results2': response2,
                'results3': response3,
                'results4': response4,
            }
            return render(request, 'tech_task_analysis.html', context)
    except Exception as e:
        logger.error("Error in tech_task_analysis_data view: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

from collections import OrderedDict
from django.http import JsonResponse
from django.shortcuts import render
from datetime import timedelta


import json
from django.http import JsonResponse
from django.shortcuts import render
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

def build_analysis_data(request):
    try:
        # Extract start_date and end_date from POST data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Attempt to parse filters from POST data
        filters = {}
        try:
            filters = json.loads(request.POST.get('filters', '{}'))
        except json.JSONDecodeError as e:
            logger.error("JSONDecodeError: %s", e)

        # Extract statuses from filters
        statuses = filters.get('status', [])
        strategist_names = filters.get('strategist_name', [])

        # Prepare filter conditions and parameters
        filter_conditions = []
        params = [start_date, end_date]

        def handle_empty_string(value):
            return None if value == '' else value

        # Add status filter conditions if statuses are provided
        if statuses:
            filter_conditions.append('"Status" IN %s')
            params.append(tuple(handle_empty_string(x) for x in statuses if x))
        if strategist_names:
            filter_conditions.append('"Strategist Name" IN %s')
            params.append(tuple(handle_empty_string(x) for x in strategist_names if x))

        # Join filter conditions
        filter_sql = ' AND '.join(filter_conditions)    

        # SQL query for weekly data
        query1 = f"""
            SELECT
                DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) AS week_start,
                (DATE_TRUNC('week', TO_DATE("Date", 'YYYY-MM-DD')) + INTERVAL '6 days') AS week_end,
                "Status",
                COUNT(*) AS total_leads
            FROM "Build"
            WHERE "Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY week_start, week_end, "Status"
            ORDER BY week_start, "Status";
        """
        results1 = execute_raw_sql(query1, params)

        # SQL query for status-wise data
        query2 = f"""
            SELECT
                "Status",
                COUNT(*) AS count
            FROM "Build"
            WHERE "Date" BETWEEN %s AND %s
            {f"AND {filter_sql}" if filter_sql else ""}
            GROUP BY "Status"
            ORDER BY "Status";
        """
        results2 = execute_raw_sql(query2, params)

        # Prepare data for weekly status chart
        weekly_data = OrderedDict()
        status_labels = ['Open', 'In Progress', 'Hold', 'Resolved']

        for row in results1:
            week_start = row[0].strftime('%Y-%m-%d')
            week_end = row[1].strftime('%Y-%m-%d')
            status = row[2]
            total_leads = row[3]

            week_label = f'{week_start} - {week_end}'

            if week_label not in weekly_data:
                weekly_data[week_label] = {status: 0 for status in status_labels}
            
            weekly_data[week_label][status] += total_leads
            
        response1 = {
            'labels': list(weekly_data.keys()),
            'datasets': [
                {
                    'label': status,
                    'data': [weekly_data[week].get(status, 0) for week in weekly_data],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                } for status in status_labels
            ]
        }
        
        # Prepare data for status pie chart
        status_data = {row[0]: row[1] for row in results2}
        
        response2 = {
            'labels': list(status_data.keys()),
            'datasets': [{
                'data': list(status_data.values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        }

        # Check if request is AJAX and respond accordingly
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'results1': response1,
                'results2': response2,
            }
            return JsonResponse(data)
        else:
            # Render the data in the template for non-AJAX requests
            context = {
                'start_date': start_date,
                'end_date': end_date,
                'results1': response1,
                'results2': response2,
            }
            return render(request, 'build_analysis.html', context)
    except Exception as e:
        logger.error("Error in build_analysis_data view: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

from django.http import JsonResponse

def fetch_employee_ids(request):
    try:
        query = 'SELECT DISTINCT "Sales Employee ID" FROM "Sales";'
        employee_ids = execute_raw_sql(query, [])
        employee_ids = [row[0] for row in employee_ids]
        return JsonResponse({'employee_ids': employee_ids})
    except Exception as e:
        logger.error("Error fetching employee IDs: %s", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def sales_filter(request, column, value):
    employee_id = None
    # name = None
    algobulls_employee = None
    branch_employee = None
    
    # First, try to find the user in the AlgobullsEmployee table
    try:
        algobulls_employee = AlgobullsEmployee.objects.get(email_id=request.user.username)
        employee_id = algobulls_employee.employee_id
        # name = algobulls_employee.name
    except AlgobullsEmployee.DoesNotExist:
        # If not found, try to find the user in the BranchEmployee table
        try:
            branch_employee = BranchEmployee.objects.get(email_id=request.user.username)
            employee_id = branch_employee.branch_employee_id
            # name = branch_employee.name
        except BranchEmployee.DoesNotExist:
            employee_id = None
            # name = None

    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fetch user permissions
    user_permissions = []
    for group in user_groups:
        user_permissions.extend(group.permissions.all())
    
    sales_leads = Sales.objects.filter().order_by('lead_id')
    number_of_sales_status = sales_leads.count()
    
    branch_employees = BranchEmployee.objects.all()
    sales_employees = AlgobullsEmployee.objects.all()
    # name = algobulls_employee.name
    user_group = user_groups[0].name
    
    # Fetch the name of the first user group
    if user_group == "Branch Employee":
        sales_leads = sales_leads.filter(branch_employee_id=employee_id)
        number_of_sales_status = sales_leads.count()
        
    if user_group == "Branch Head":
        head_branch_id = branch_employee.branch_id
        sales_leads = sales_leads.filter(branch_employee_id__branch_id=head_branch_id)
        number_of_sales_status = sales_leads.count()
        
    if user_group == "Sales Employee":
        sales_leads = sales_leads.filter(sales_employee_id=employee_id)
        number_of_sales_status = sales_leads.count()
    
    context = {
        'user_groups': user_groups,
        'user_permissions': user_permissions,
        'permissions_name': [i.name for i in user_permissions],
        'employee_id': employee_id,
        "sales_leads": sales_leads,
        "role_name": user_group,  # Replace "Sales Head" with user_group
        # "name": name,
        'branch_employees': branch_employees,
        'sales_employees' : sales_employees,
        'number_of_sales_status':number_of_sales_status,
        
    }
    
    return render(request, 'sales.html', context)
from django.http import JsonResponse
from django.db.models import Q

def apply_filters(request):
    if request.method == 'POST' and request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Process the AJAX request
        filters = request.POST.dict()  # Assuming filters are sent as POST data
        # Construct Q objects for filtering
        q_objects = Q()
        for key, value in filters.items():
            q_objects |= Q(**{key: value})
        # Query the Sales model with the constructed Q objects
        sales_leads = Sales.objects.filter(q_objects).values()
        # Return JSON response with filtered data
        return JsonResponse({'status': 'success', 'data': list(sales_leads)})
    else:
        # Handle non-AJAX or GET request
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})
