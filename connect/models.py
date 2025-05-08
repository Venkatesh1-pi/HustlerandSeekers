from django.db import models

# Create your models here.

class Connect(models.Model):

	user_id=models.CharField(max_length=100, null=True, blank=True)
	hustler_id=models.CharField(max_length=100, null=True, blank=True)
	role_category_id=models.CharField(max_length=100, null=True, blank=True)
	status=models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Notifications(models.Model):

	connect_id=models.CharField(max_length=100, null=True, blank=True)
	user_id=models.CharField(max_length=100, null=True, blank=True)
	hustler_id=models.CharField(max_length=100, null=True, blank=True)
	role_category_id=models.CharField(max_length=100, null=True, blank=True)
	notification=models.CharField(max_length=100, null=True, blank=True)
	seeker_notification=models.CharField(max_length=100, null=True, blank=True)
	notifica_type=models.CharField(max_length=100, null=True, blank=True)
	status=models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)	

class Review(models.Model):

	user_id=models.CharField(max_length=100, null=True, blank=True)
	hustler_id=models.CharField(max_length=100, null=True, blank=True)
	role_id=models.CharField(max_length=100, null=True, blank=True)
	review=models.CharField(max_length=100, null=True, blank=True)
	rating=models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Appointments(models.Model):

	user_id=models.CharField(max_length=100, null=True, blank=True)
	hustler_id=models.CharField(max_length=100, null=True, blank=True)
	role_id=models.CharField(max_length=100, null=True, blank=True)
	date=models.DateField(auto_now=True)
	start_time=models.TimeField(default='12:00')
	end_time=models.TimeField(default='12:00')
	where=models.CharField(max_length=255, null=True, blank=True)
	hustle=models.CharField(max_length=255, null=True, blank=True)
	price=models.CharField(max_length=255, null=True, blank=True)
	modified_by=models.CharField(max_length=255, null=True, blank=True)
	status=models.CharField(max_length=255, null=True, blank=True)
	updated_at = models.DateTimeField(auto_now_add=True)		
	created_at = models.DateTimeField(auto_now_add=True)		