from django.db import models

# Create your models here.

class Questionnaire(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 200)
	own = models.CharField(max_length = 20)
	type = models.IntegerField()
	
	create_time = models.DateTimeField(auto_now_add = True, editable = False)
	#validity = models.DateTimeField()
	duration = models.IntegerField()  #  考试时长 limit_time

	count = models.IntegerField()
	hash = models.CharField(max_length = 20)

	random_order = models.BooleanField(default = False)
	select_less_score = models.BooleanField(default = False)  #  少选得分

class Info(models.Model):
	id = models.IntegerField(primary_key = True)
	state = models.IntegerField()  #  status
	upload_time = models.DateTimeField(auto_now = True)

class favorite(models.Model):
	username = models.CharField(max_length = 20)
	qid = models.IntegerField()

class Img(models.Model):
	img = models.ImageField(blank = True)
