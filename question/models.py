from django.db import models

# Create your models here.

class Question(models.Model):
	id = models.AutoField(primary_key = True)
	questionnaire_id = models.IntegerField()
	rank = models.IntegerField()
	type = models.IntegerField()
	content = models.TextField()
	is_required = models.BooleanField(default = False)
	description = models.TextField(null = True, blank = True)
	option = models.TextField(null = True, blank = True)