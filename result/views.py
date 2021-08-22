from django.http import JsonResponse
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from result.models import *
from QPlanet.values import *
import datetime
import json
# Create your views here.

@csrf_exempt
def submit(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = int(data_json['qid'])
		results = data_json['results']
		total = SubmitInfo.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 0
		else:
			total = int(total['id__max']) + 1
		
		submitinfo = SubmitInfo(id = total, qid = qid, submit_time = str(datetime.datetime.now()))
		submitinfo.save()
		for i in results:
			submit = Submit(sid = total, problem_id = int(i['problem_id']), type = int(i['type']), answer = i['answer'])
			submit.save()
		
		return JsonResponse({'result': ACCEPT, 'message': r'提交成功!'})

@csrf_exempt
def analyze(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = int(data_json['qid'])
		'''
		{
			qid:
			total:
			questions:[
				{
					type:0/1,
					choice:[],
					count:[],
				},
				{
					type:1
					choice:[]
					url:[]
				},
				{},
			]
		}
		'''