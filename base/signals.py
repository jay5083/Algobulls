# base/signals.py
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import AlgobullsEmployee, BranchEmployee, AuthPermission, AuthRole

# Sync AuthRole with Group changes
@receiver(post_save, sender=Group)
def sync_roles_on_group_change(sender, instance, created, **kwargs):
    """Sync AuthRole table on Group creation or update"""
    role_id = str(instance.id)
    role_name = instance.name

    if created:
        AuthRole.objects.create(role_id=role_id, role_name=role_name)
    else:
        AuthRole.objects.update_or_create(
            role_id=role_id,
            defaults={'role_name': role_name}
        )

@receiver(post_delete, sender=Group)
def delete_role_on_group_delete(sender, instance, **kwargs):
    """Delete AuthRole entry when a Group is deleted"""
    role_id = str(instance.id)
    try:
        role = AuthRole.objects.get(role_id=role_id)
        role.delete()
    except AuthRole.DoesNotExist:
        print(f"No role found for deleted group {role_id}")

@receiver(post_save, sender=User)
def sync_employee_on_user_save(sender, instance, created, **kwargs):
    employee_type = get_employee_type(instance)

    if employee_type == 'Algobulls Employee':
        AlgobullsEmployee.objects.update_or_create(
            employee_id=str(instance.id),
            defaults={
                'email_id': instance.email,
                'password': instance.password,
                'name': f"{instance.first_name} {instance.last_name}",
                # Add other fields here as needed
            }
        )
    elif employee_type == 'Branch Employee':
        BranchEmployee.objects.update_or_create(
            branch_employee_id=str(instance.id),
            defaults={
                'email_id': instance.email,
                'password': instance.password,
                'name': f"{instance.first_name} {instance.last_name}",
                # Add other fields here as needed
            }
        )
    else:
        print(f"User {instance.username} does not have a valid employee type.")

    update_user_roles(instance)

@receiver(post_delete, sender=User)
def delete_employee_on_user_delete(sender, instance, **kwargs):
    AlgobullsEmployee.objects.filter(employee_id=str(instance.id)).delete()
    BranchEmployee.objects.filter(branch_employee_id=str(instance.id)).delete()

@receiver(m2m_changed, sender=User.groups.through)
def sync_user_groups(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Sync AlgobullsEmployee and BranchEmployee when user's groups change"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        update_user_roles(instance)

def update_user_roles(user):
    """Update employee roles in AlgobullsEmployee and BranchEmployee"""
    role_instance = None
    if user.groups.exists():
        group = user.groups.first()  # Assuming you only want the first group
        role_instance = AuthRole.objects.filter(role_id=str(group.id)).first()

    employee_type = get_employee_type(user)

    if employee_type == 'Algobulls Employee':
        AlgobullsEmployee.objects.filter(employee_id=str(user.id)).update(
            role_id=role_instance
        )
    elif employee_type == 'Branch Employee':
        BranchEmployee.objects.filter(branch_employee_id=str(user.id)).update(
            role=role_instance
        )

def get_employee_type(user):
    """Get the employee type from AuthPermission model."""
    try:
        auth_permission = AuthPermission.objects.get(user=user)
        return auth_permission.employee_type
    except AuthPermission.DoesNotExist:
        print(f"No AuthPermission found for user {user.username}")
        return None

    
import random
import string
import pyotp
import qrcode
import base64
from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def generate_qr_code_base64(uri):
    qr = qrcode.make(uri)
    buffered = BytesIO()
    qr.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import pyotp
import qrcode
import random
import string
import base64
from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        instance.set_password(password)
        instance.save()

        # Encode the username to base32
        key = base64.b32encode(instance.username.encode('utf-8')).decode('utf-8')
        
        # Create a TOTP object with the key
        totp = pyotp.TOTP(key)
        
        # Generate QR code for the user's TOTP provisioning URI
        uri = totp.provisioning_uri(name=instance.username, issuer_name="Algobulls")
        qr_code = qrcode.make(uri)
        
        # Save the QR code to a BytesIO buffer
        buffered = BytesIO()
        qr_code.save(buffered, 'PNG')
        
        # Reset buffer position to the beginning
        buffered.seek(0)

        # Email subject and content
        subject = 'Welcome to Algobulls'
        context = {
            'username': instance.username,
            'password': password,
            'qr_code': base64.b64encode(buffered.getvalue()).decode('utf-8'),  # Base64 for HTML embedding
        }
        html_message = render_to_string('welcome_email.html', context)
        plain_message = strip_tags(html_message)
        recipient_list = [instance.username]  # Use the user's email

        # Create email with attachment
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email='jay2004.1729@gmail.com',
            to=recipient_list
        )
        email.attach_alternative(html_message, "text/html")
        email.attach('totp.png', buffered.getvalue(), 'image/png')  # Attach QR code as PNG

        # Send email
        try:
            email.send()
        except Exception as e:
            print(f"Failed to send email: {e}") 
            
# your_app/signals.py

import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import AuthPermission

@receiver(pre_save, sender=AuthPermission)
def set_unique_permission_id(sender, instance, **kwargs):
    # Only set if the permission_id is not already set
    if not instance.permission_id:
        instance.permission_id = str(uuid.uuid4())
