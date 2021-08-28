from django.db import models

# Create your models here.

class Questionnaire(models.Model):
	id = models.IntegerField(primary_key = True)
	title = models.CharField(max_length = 50)
	description = models.CharField(max_length = 200, null = True, blank = True)
	own = models.CharField(max_length = 20)
	type = models.IntegerField(default = 0)
	
	create_time = models.DateTimeField(auto_now_add = True, editable = False)
	deadline = models.DateTimeField(null = True, blank = True)
	duration = models.IntegerField(null = True, blank = True)  #  考试时长

	quota = models.IntegerField(null = True, blank = True)
	count = models.IntegerField()
	hash = models.CharField(max_length = 20)

	random_order = models.BooleanField(default = False)
	select_less_score = models.BooleanField(default = False)  #  少选得分
	certification = models.IntegerField(default = 0)
	show_number = models.BooleanField(default = True)		  #  显示题号

class Info(models.Model):
	id = models.IntegerField(primary_key = True)
	state = models.IntegerField()
	upload_time = models.DateTimeField(auto_now = True)

class favorite(models.Model):
	username = models.CharField(max_length = 20)
	qid = models.IntegerField()
