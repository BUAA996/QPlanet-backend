from django.db import models

# Create your models here.

class Question(models.Model):
	id = models.AutoField(primary_key = True)
	questionnaire_id = models.IntegerField()
	rank = models.IntegerField()
	type = models.IntegerField()
	content = models.TextField()
	is_required = models.BooleanField(default = False)
	is_essential = models.BooleanField(default = False)
	description = models.TextField()
	extra = models.TextField()

class StandardAnswer(models.Model):
	qid = models.IntegerField()
	type = models.IntegerField()
	content = models.TextField()
	score = models.IntegerField()