from django.http import JsonResponse
from django.shortcuts import render
from questionnaire.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from QPlanet.values import *
import json
import datetime
# Create your views here.

@csrf_exempt
def create(request):
	if request.method == 'POST':
		if request.session.get('is_login') == False:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})

		data_json = json.loads(request.body)
		title = data_json['title']
		description = data_json['description']
		type = int(data_json['type'])
		limit_time = int(data_json['limit_time'])
		# validity = int(data_json['validity'])
		# TODO load time
		validity = datetime.datetime.now()
		username = request.session.get('user')
		questions =  data_json['questions']
		# save_questions(questions)
		# TODO save the questions

		total = Questionnaire.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 1
		else:
			total = int(total['id__max']) + 1
		
		questionnaire = Questionnaire(
			id=total, title=title, description=description, type=type, own = username,
			 validity = validity, limit_time=limit_time, create_time = str(datetime.datetime.now()),
			upload_time = "", count = 0, status = SAVED, hash = ""
		)

		questionnaire.save()
		return JsonResponse({'result': ACCEPT, 'message': r'保存成功!'})