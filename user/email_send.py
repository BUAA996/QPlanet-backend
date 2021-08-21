from random import Random  				# 用于生成随机码
from django.core.mail import send_mail  # 发送邮件模块
from django.conf import settings		# setting.py添加的的配置信息
from user.models import *

import datetime

# 生成随机字符串
def random_str(randomlength=8):
	str = ''
	chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
	length = len(chars) - 1
	random = Random()
	for i in range(randomlength):
		str += chars[random.randint(0, length)]
	return str

def send_code_email(email):
	code = random_str(16)
	NewCode = Code()
	NewCode.code = code
	NewCode.save()

	email_title = "问卷星球注册激活验证码"
	email_body = "欢迎您注册问卷星球!\n"
	email_body += "您的邮箱注册验证码为：{0}, 该验证码有效时间为两分钟，请及时进行验证.\n".format(code)
	email_body += "如果您从未注册过问卷星球,请忽略该邮件."

	send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
	return send_status

def SendPasswordCodeEmail(email):
	code = random_str(6)
	NewCode = Code()
	NewCode.code = code
	NewCode.save()

	email_title = "问卷星球密码重置验证码"
	email_body = "您的密码重置验证码为：{0}, 该验证码有效时间为两分钟，请及时修改密码.\n".format(code)
	email_body += "如果您从未注册过问卷星球,请忽略该邮件."

	send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
	return send_status

def check_code(code):
	if Code.objects.filter(code=code).exists() == False:
		return False
	else:
		Code.objects.filter(code=code).delete()
		return True