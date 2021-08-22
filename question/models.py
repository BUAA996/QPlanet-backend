from django.db import models

# Create your models here.

class Question(models.Model):
	id = models.IntegerField(primary_key = True)
	qid = models.IntegerField()
	rank = models.IntegerField()
	username  = models.CharField(max_length = 50)
	type = models.IntegerField()
	title = models.TextField()
	must = models.IntegerField()
	choise = models.TextField()