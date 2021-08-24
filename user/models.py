from django.db import models
# from captcha.fields import CaptchaField

# Create your models here.
class Main(models.Model):
	id = models.IntegerField(primary_key = True)
	username = models.CharField(max_length = 20)
	password = models.CharField(max_length = 20)
	email = models.EmailField()

class Code(models.Model):
	code = models.CharField(max_length = 100)