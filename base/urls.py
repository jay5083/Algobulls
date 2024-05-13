from django.urls import path, include
from .views import home, update_sales_leads, delete_sales, add_sales_leads, add_build, add_tech_task, add_support, add_strategies, delete_strategy, delete_support
from . import views

urlpatterns = [ 
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/profile/', home, name='home'),
    path('update_sales_leads/', update_sales_leads, name='update_sales_leads'),
    path('accounts/profile/add_sales_leads/', add_sales_leads, name='add_sales_leads'),  
    path('delete_sales/', delete_sales, name='delete_sales'), 
    path('accounts/profile/add_build/', add_build, name='add_build'),
    path('accounts/profile/add_tech_task/', add_tech_task, name='add_tech_task'), 
    path('accounts/profile/add_support/', add_support, name='add_support'),
    path('accounts/profile/add_strategies/', add_strategies, name='add_strategies'),
    path('delete_strategy/', delete_strategy, name='delete_strategy'),
    path('delete_support/', views.delete_support, name='delete_support'),
    path('delete_tech_task/', views.delete_tech_task, name='delete_tech_task'),
    path('delete_build/', views.delete_build, name='delete_build'),
    path('update_build/', views.update_build, name='update_build'),
    path('update_tech_task/', views.update_tech_task, name='update_tech_task'),
    path('update_support/', views.update_support, name='update_support'),
    path('update_strategies/', views.update_strategies, name='update_strategies'),
]
