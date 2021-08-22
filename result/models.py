from django.db import models

# Create your models here.

class SubmitInfo(models.Model):
	id = models.IntegerField(primary_key = True)
	qid = models.IntegerField()
	submit_time = models.CharField(max_length = 50)
	author = models.CharField(max_length = 50, null=True, blank=True)

class Submit(models.Model):
	sid = models.IntegerField()
	problem_id = models.IntegerField()
	type = models.IntegerField()
	answer = models.TextField(null=True, blank=True)