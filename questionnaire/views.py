from django.http import JsonResponse
from django.shortcuts import render
from questionnaire.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from QPlanet.values import *
import json
import datetime
import random
import string
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
		return JsonResponse({'result': ACCEPT, 'message': r'保存成功!', 'qid':total})

@csrf_exempt
def list(request):
	if request.method == 'POST':
		if request.session.get('is_login') == False:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		username = request.session.get('user')
		l = [x for x in Questionnaire.objects.filter(own = username)]
		l.sort(key = lambda x: x.id)
		l.reverse()
		result = {'result': ACCEPT, 'message': r'获取成功!', 'questionnaires':[]}
		for x in l:
			if x.status == DELETED:
				continue
			d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
				'create_time':x.create_time, 'count':x.count, 'hash':x.hash}
			result['questionnaires'].append(d)
		return JsonResponse(result)



def hash(id):
	q = Questionnaire.objects.get(id = id)
	q.hash = ''.join(random.sample(string.ascii_letters + string.digits, 8))
	q.save()
	return q.hash

@csrf_exempt
def reset_hash(request):
	if request.method == 'POST':
		if request.session.get('is_login') == False:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		new = hash(id)

		return JsonResponse({'result': ACCEPT, 'message':r'重置成功!', 'hash':new})

@csrf_exempt
def delete(request):
	if request.method == 'POST':
		if request.session.get('is_login') == False:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		q = Questionnaire.objects.get(id = id)
		if q.status == DELETED:
			# TODO : clear the information about this questionnaire
			q.delete()
			return JsonResponse({'result': ACCEPT, 'message':r'已彻底删除该问卷!'})
		else:
			q.status = DELETED
			q.save()
			return JsonResponse({'result': ACCEPT, 'message':r'已将该问卷移动至回收站!'})

@csrf_exempt
def recover(request):
	if request.method == 'POST':
		if request.session.get('is_login') == False:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		q = Questionnaire.objects.get(id = id)
		q.status = SAVED
		q.save()
		return JsonResponse({'result': ACCEPT, 'message':r'已恢复!'})