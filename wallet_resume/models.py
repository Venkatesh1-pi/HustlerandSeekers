from django.db import models

# Create your models here.

class ResumeWallet(models.Model):

	user_id=models.CharField(max_length=100, null=True, blank=True)
	role_category_id=models.CharField(max_length=100, null=True, blank=True)
	role_category_name=models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)