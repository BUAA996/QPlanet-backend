from django.db import models

# Create your models here.

class Questionnaire(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 50)
	own = models.CharField(max_length = 20)
	type = models.IntegerField()
	
	create_time = models.CharField(max_length = 50)
	upload_time = models.CharField(max_length = 50)
	validity = models.DateTimeField()
	limit_time = models.IntegerField()

	count = models.IntegerField()
	status = models.IntegerField()
	hash = models.CharField(max_length = 20)


class Paper(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 50)
	own = models.CharField(max_length = 20)
	type = models.IntegerField()
	
	create_time = models.CharField(max_length = 50)
	upload_time = models.CharField(max_length = 50)
	validity = models.DateTimeField()
	limit_time = models.IntegerField()

	count = models.IntegerField()
	status = models.IntegerField()
	hash = models.CharField(max_length = 20)
