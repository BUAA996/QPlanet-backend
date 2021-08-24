from django.db import models

# Create your models here.

class Questionnaire(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 200)
	own = models.CharField(max_length = 20)
	type = models.IntegerField()
	
	create_time = models.CharField(max_length = 50)
	validity = models.DateTimeField()
	limit_time = models.IntegerField()

	count = models.IntegerField()
	hash = models.CharField(max_length = 20)

class Info(models.Model):
	id = models.IntegerField(primary_key = True)
	status = models.IntegerField()
	upload_time = models.CharField(max_length = 50)

class Img(models.Model):
	img = models.ImageField(blank = True)

class Paper(models.Model):
	id = models.IntegerField(primary_key = True)
