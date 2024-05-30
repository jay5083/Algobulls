import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algobulls.settings')
django.setup()

def send_test_email():
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['jaychaudhari.ecell@gmail.com']
    send_mail(subject, message, "jay2007.1729@gmail.com", recipient_list)

# Optionally call the function for testing
if __name__ == '__main__':
    send_test_email()

