from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from user.models import *
from QPlanet.values import *
from user.email_send import *
import re
import json
# Create your views here.

@csrf_exempt
def register(request):
	if request.method == 'POST':
		if request.session.get('is_login') == True:
			return JsonResponse({'result': ERROR, 'message': r'已登录!'})
				
		data_json = json.loads(request.body)
		username = data_json.get('username')
		password1 = data_json.get('password1')
		password2 = data_json.get('password2')
		email = data_json.get('email')
		code = data_json.get('code')

		if Main.objects.filter(username=username).exists():
			return JsonResponse({'result': ERROR, 'message': r'用户已存在!'})
		
		pattern = re.compile(r'^[0-9a-zA-z].+@buaa.edu.cn$')
		if pattern.search(email) == None:
			return JsonResponse({'result': ERROR, 'message': r'邮箱格式错误!'})
		pattern = re.compile(r'^[0-9a-zA-Z]{6,16}$')
		if pattern.search(password1) == None:
			return JsonResponse({'result': ERROR, 'message': r'密码格式错误!'})
		
		if password1 != password2:
			return JsonResponse({'result': ERROR, 'message': r'密码不匹配!'})
		
		if check_code(code) == False:
			return JsonResponse({'result': ERROR, 'message': r'验证码不存在!'})
		
		total = Main.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 0
		else:
			total = int(total['id__max'])

		user = Main(id=total+1, username=username, password=password1, email=email)
		user.save()
		return JsonResponse({'result': ACCEPT, 'message': r'注册成功!'})

@csrf_exempt
def login(request):
	if request.method == 'POST':
		if request.session.get('is_login') == True:
			return JsonResponse({'result': ERROR, 'message': r'已登录!'})
		data_json = json.loads(request.body)
		username = data_json.get('username')
		password = data_json.get('password')
		if Main.objects.filter(username=username).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'用户不存在!'})
			
		user = Main.objects.get(username=username)
		if user.password != password:
			return JsonResponse({'result': ERROR, 'message': r'密码错误!'})
		request.session['is_login'] = True
		request.session['user'] = username
		return JsonResponse({'result': ACCEPT, 'message': r'登录成功!'})

@csrf_exempt
def logout(request):
	if request.method == 'POST':
		if request.session.get('is_login', 0) != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		request.session.flush()
		return JsonResponse({'result': ACCEPT, 'message': r'登出成功!'})

@csrf_exempt
def is_login(request):
	if request.session.get('is_login', 0) != True:
		return JsonResponse({'result': ERROR})
	else:
		return JsonResponse({'result': ACCEPT})

@csrf_exempt
def send_code(request):
	if request.method == 'POST':
		if request.session.get('is_login') == True:
			return JsonResponse({'result': ERROR, 'message': r'已登录!'})
		
		data_json = json.loads(request.body)
		email = data_json.get('email')
		pattern = re.compile(r'^[0-9a-zA-z].+@buaa.edu.cn$')
		if pattern.search(email) == None:
			return JsonResponse({'result': ERROR, 'message': r'邮箱格式错误!'})
		
		send_code_email(email)
		return JsonResponse({'result': ACCEPT, 'message': r'发送成功!'})

@csrf_exempt
def get_captcha(request):
	if request.method == 'POST':
		data = {}
		data['new_cptch_key'] = CaptchaStore.generate_key()
		data['new_cptch_image'] = captcha_image_url(data['new_cptch_key'])
		captcha = CaptchaStore.objects.get(hashkey = data['new_cptch_key'])
		data['key'] = captcha.response
		return JsonResponse(data)