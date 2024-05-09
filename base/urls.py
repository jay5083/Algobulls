from django.urls import path, include
from .views import home

urlpatterns = [ 
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/profile/', home, name='home'),
    
]

