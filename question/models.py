from django.db import models

# Create your models here.

class Question(models.Model):
	id = models.AutoField(primary_key = True)
	questionaire_id = models.IntegerField()
	rank = models.IntegerField()
	username  = models.CharField(max_length = 50)
	type = models.IntegerField()
	content = models.TextField()
	is_required = models.BooleanField(default = False)
	option = models.TextField(null = True, blank = True)