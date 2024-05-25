from django.urls import path, include
from .views import home, update_sales_leads, delete_sales, add_sales_leads, add_build, add_tech_task, add_support, add_strategies, delete_strategy, delete_support
from . import views

urlpatterns = [ 
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/profile/', home, name='home'),
    path('update_sales_leads/', update_sales_leads, name='update_sales_leads'),
    path('accounts/profile/sales/add_sales_leads/', add_sales_leads, name='sales/add_sales_leads'),  
    path('delete_sales/', delete_sales, name='delete_sales'), 
    path('accounts/profile/add_build/', add_build, name='add_build'),
    path('accounts/profile/add_tech_task/', add_tech_task, name='add_tech_task'), 
    path('accounts/profile/add_support/', add_support, name='add_support'),
    path('accounts/profile/add_strategies/', add_strategies, name='add_strategies'),
    path('accounts/profile/add_rms/', views.add_rms, name='add_rms'),
    path('delete_strategy/', delete_strategy, name='delete_strategy'),
    path('delete_support/', views.delete_support, name='delete_support'),
    path('delete_tech_task/', views.delete_tech_task, name='delete_tech_task'),
    path('delete_build/', views.delete_build, name='delete_build'),
    path('update_build/', views.update_build, name='update_build'),
    path('update_tech_task/', views.update_tech_task, name='update_tech_task'),
    path('update_support/', views.update_support, name='update_support'),
    path('update_strategies/', views.update_strategies, name='update_strategies'),
    path('update_rms/', views.update_rms, name='update_rms'),
    path('update_sales/', views.update_sales, name='update_sales'),
    path('get_division_employees/', views.get_division_employees, name='get_division_employees'),
    path('get_status_values/<str:table>/', views.get_status_values, name='get_status_values'),
    path('get_status_values/<str:table>/', views.get_status_values, name='get_status_values'),
    path('filter_by_status/<str:table>/<str:status>/', views.status_filter, name='filter_by_status'),
    path('sales-leads/', views.sales, name='sales-leads'),
    path('support/', views.support, name='support'),
    path('build/', views.build, name='build'),
    path('strategies/', views.strategies, name='strategies'),
    path('tech_task/', views.tech_task, name='tech_task'),
    path('rms/', views.rms, name='rms'),
    path('sales_analysis_data/', views.sales_analysis_data, name='sales_analysis_data'),
    path('to_sales_analysis/', views.to_sales_analysis, name='to_sales_analysis'),
    path('sales_filter/', views.sales_filter, name='sales_filter'),
    path('apply_filters/', views.apply_filters, name='apply_filters'),
    path('fetch_employee_ids/', views.fetch_employee_ids, name='fetch_employee_ids'),
]

    

