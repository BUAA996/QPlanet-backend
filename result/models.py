from django.db import models

# Create your models here.

class SubmitInfo(models.Model):
	id = models.IntegerField(primary_key = True)
	qid = models.IntegerField()
	submit_time = models.DateTimeField(auto_now_add = True, editable = False)
	author = models.CharField(max_length = 50, null = True, blank = True)
	score = models.FloatField(null = True, blank = True)

class Submit(models.Model):
	sid = models.IntegerField()
	problem_id = models.IntegerField()
	type = models.IntegerField()
	answer = models.TextField(null = True, blank = True)

class Phone(models.Model):
	phone_number = models.CharField(max_length = 11)
	captcha = models.CharField(max_length = 6)
	sid = models.IntegerField(null = True, blank = True)
	qid = models.IntegerField(null = True, blank = True)
	# order 