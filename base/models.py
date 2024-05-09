# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AlgobullsDivision(models.Model):
    division_name = models.TextField(db_column='Division Name', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Algobulls Division'


class AlgobullsEmployee(models.Model):
    employee_id = models.TextField(db_column='Employee ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    email_id = models.TextField(db_column='Email ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    password = models.TextField(db_column='Password', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    division_name = models.ForeignKey(AlgobullsDivision, models.DO_NOTHING, db_column='Division Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    role_id = models.ForeignKey('AuthRole', models.DO_NOTHING, db_column='Role ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Algobulls Employee'


class AuthPermission(models.Model):
    permission_id = models.TextField(db_column='Permission ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    permission_name = models.TextField(db_column='Permission Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Auth Permission'


class AuthRole(models.Model):
    role_id = models.TextField(db_column='Role ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    role_name = models.TextField(db_column='Role Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Auth Role'


class Branch(models.Model):
    branch_id = models.TextField(db_column='Branch ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    broker_id = models.ForeignKey('Broker', models.DO_NOTHING, db_column='Broker ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Branch'


class BranchEmployee(models.Model):
    branch_employee_id = models.TextField(db_column='Branch Employee ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    email_id = models.TextField(db_column='Email ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    password = models.TextField(db_column='Password', blank=True, null=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    role = models.TextField(db_column='Role', blank=True, null=True)  # Field name made lowercase.
    branch_id = models.ForeignKey(Branch, models.DO_NOTHING, db_column='Branch ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Branch Employee'


class Broker(models.Model):
    broker_id = models.TextField(db_column='Broker ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    broker_name = models.TextField(db_column='Broker Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Broker'


class Build(models.Model):
    build_id = models.TextField(db_column='Build ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    strategist_name = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Strategist Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    strategist_number = models.TextField(db_column='Strategist Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    email_id = models.TextField(db_column='Email ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    strategy = models.TextField(db_column='Strategy', blank=True, null=True)  # Field name made lowercase.
    document = models.TextField(db_column='Document', blank=True, null=True)  # Field name made lowercase.
    payment_date = models.TextField(db_column='Payment Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    payment_amount = models.TextField(db_column='Payment Amount', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    delivery_date = models.TextField(db_column='Delivery Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    source = models.TextField(db_column='Source', blank=True, null=True)  # Field name made lowercase.
    assign_from = models.TextField(db_column='Assign From', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    manage_by = models.TextField(db_column='Manage By', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Build'


class PermissionAccessTable(models.Model):
    role_id = models.ForeignKey(AuthRole, models.DO_NOTHING, db_column='Role ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    permission_id = models.ForeignKey(AuthPermission, models.DO_NOTHING, db_column='Permission ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Permission Access Table'


class Sales(models.Model):
    lead_id = models.TextField(db_column='Lead ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    branch_employee_id = models.ForeignKey(BranchEmployee, models.DO_NOTHING, db_column='Branch Employee ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    broking_id = models.TextField(db_column='Broking ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    contact_number = models.TextField(db_column='Contact Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    email_id = models.TextField(db_column='Email ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    source_type = models.TextField(db_column='Source Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    risk_appetite = models.TextField(db_column='Risk Appetite', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    comments = models.TextField(db_column='Comments', blank=True, null=True)  # Field name made lowercase.
    amount = models.TextField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    purchase_date = models.TextField(db_column='Purchase Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    status = models.TextField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    reason_for_dropped = models.TextField(db_column='Reason For Dropped', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sales_employee_id = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Sales Employee ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Sales'


class Strategies(models.Model):
    strategy_id = models.TextField(db_column='Strategy ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employee_id = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Employee ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    mobile_number = models.TextField(db_column='Mobile Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    broking_house = models.TextField(db_column='Broking House', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    client_id = models.TextField(db_column='Client ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Strategies'


class Support(models.Model):
    ticket_number = models.TextField(db_column='Ticket Number', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    branch_employee_id = models.ForeignKey(BranchEmployee, models.DO_NOTHING, db_column='Branch Employee ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    broking_id = models.TextField(db_column='Broking ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    contact_number = models.TextField(db_column='Contact Number', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    email_id = models.TextField(db_column='Email ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    date_of_error = models.TextField(db_column='Date Of Error', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    strategy_code = models.TextField(db_column='Strategy Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    strategy_instrument = models.TextField(db_column='Strategy Instrument', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    customer_type = models.TextField(db_column='Customer Type', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    priority = models.TextField(db_column='Priority', blank=True, null=True)  # Field name made lowercase.
    issue = models.TextField(db_column='Issue', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    support_employee = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Support Employee', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    division_employee = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Division Employee', related_name='support_division_employee_set', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    status = models.TextField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    date_of_closing = models.TextField(db_column='Date of Closing', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'Support'


class TechTask(models.Model):
    task_id = models.TextField(db_column='Task ID', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employee_id = models.ForeignKey(AlgobullsEmployee, models.DO_NOTHING, db_column='Employee ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    task = models.TextField(db_column='Task', blank=True, null=True)  # Field name made lowercase.
    nature = models.TextField(db_column='Nature', blank=True, null=True)  # Field name made lowercase.
    task_status = models.TextField(db_column='Task Status', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    priority = models.TextField(db_column='Priority', blank=True, null=True)  # Field name made lowercase.
    date_of_closing = models.TextField(db_column='Date of Closing', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    number_of_days = models.TextField(db_column='Number Of Days', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    comments = models.TextField(db_column='Comments', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tech Task'
