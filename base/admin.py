from django.contrib import admin
from .models import AlgobullsDivision, AlgobullsEmployee, AuthPermission, AuthRole, Branch, BranchEmployee, Broker, Build, PermissionAccessTable, Sales, Strategies, Support, TechTask, Rms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.register(AlgobullsDivision)
admin.site.register(AlgobullsEmployee)
admin.site.register(AuthPermission)
admin.site.register(AuthRole)
admin.site.register(Branch)
admin.site.register(BranchEmployee)
admin.site.register(Broker)
admin.site.register(Build)
admin.site.register(PermissionAccessTable)
admin.site.register(Sales)
admin.site.register(Strategies)
admin.site.register(Support)
admin.site.register(TechTask)
admin.site.register(Rms)