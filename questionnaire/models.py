from django.db import models

# Create your models here.

class Questionnaire(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 200)
	own = models.CharField(max_length = 20)
	type = models.IntegerField()
	
	create_time = models.DateTimeField(auto_now_add = True, editable = False)
	deadline = models.DateTimeField()
	duration = models.IntegerField()  #  考试时长

	count = models.IntegerField()
	hash = models.CharField(max_length = 20)

	random_order = models.BooleanField(default = False)
	select_less_score = models.BooleanField(default = False)  #  少选得分
	certification = models.IntegerField()
	show_number = models.BooleanField(default = True)		  #  显示题号

class Info(models.Model):
	id = models.IntegerField(primary_key = True)
	state = models.IntegerField()  #  status
	upload_time = models.DateTimeField(auto_now = True)

class favorite(models.Model):
	username = models.CharField(max_length = 20)
	qid = models.IntegerField()
