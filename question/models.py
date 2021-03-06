from django.db import models

class Question(models.Model):
	id = models.AutoField(primary_key = True)
	questionnaire_id = models.IntegerField()
	rank = models.IntegerField()
	type = models.IntegerField()
	content = models.TextField()
	is_required = models.BooleanField(default = False)
	is_essential = models.BooleanField(default = False)
	description = models.TextField(null = True, blank = True)
	extra = models.TextField(null = True, blank = True)

class StandardAnswer(models.Model):
	qid = models.IntegerField()  #  question id
	type = models.IntegerField()
	content = models.TextField()
	score = models.IntegerField()

class Jump(models.Model):
	qid = models.IntegerField()
	next = models.TextField(null = True, blank = True)