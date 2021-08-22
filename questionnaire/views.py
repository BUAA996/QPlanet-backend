from django.http import JsonResponse
from django.shortcuts import render
from questionnaire.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
from django.utils import timezone
from QPlanet.values import *
from QPlanet.settings import *
import qrcode
import json
import datetime
import random
import string
from django import utils
from django.db.models import Q
# Create your views here.

@csrf_exempt
def create(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
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
			count = 0, hash = ""
		)
		questionnaire.save()
		
		info = Info(id = total, status = SAVED, upload_time = "")
		info.save()
		return JsonResponse({'result': ACCEPT, 'message': r'保存成功!', 'id':total})

@csrf_exempt
def list(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		username = request.session.get('user')
		l = [x for x in Questionnaire.objects.filter(own = username)]
		l.sort(key = lambda x: x.id)
		l.reverse()
		result = {'result': ACCEPT, 'message': r'获取成功!', 'questionnaires':[]}
		for x in l:
			info = Info.objects.get(id = x.id)
			if info.status == DELETED:
				continue
			d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
				'count':x.count, 'hash':x.hash, 'status':info.status,
				'create_time':x.create_time, 'upload_time':info.upload_time}
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
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		new = hash(id)

		return JsonResponse({'result': ACCEPT, 'message':r'重置成功!', 'hash':new})

@csrf_exempt
def delete(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		q = Info.objects.get(id = id)
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
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		q = Info.objects.get(id = id)
		q.status = SAVED
		q.save()
		return JsonResponse({'result': ACCEPT, 'message':r'已恢复!'})

@csrf_exempt
def release(request):
	pass
	'''
	if request.method == 'POST':
		data_json = json.loads(request.body)
		id = int(data_json['id'])

		info = Info.objects.get(id = id)
		info.status = RELEASE
		info.upload_time = datetime.datetime.now()
		info.save()

		_hash = hash(id)
		url = IMG_URL + _hash
		pic=qrcode.make(url)
		with open("img/"+_hash +".png","wb") as f:
			pic.save(f)
		image = Img(img = pic)
		image.save()

		return JsonResponse({'result': ACCEPT, 'message':r'发布成功!', 'url':url, 'img':image.img.url})

	'''
	
@csrf_exempt
def close(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		id = int(data_json['id'])

		info = Info.objects.get(id = id)
		info.status = SAVED
		info.upload_time = ""
		info.save()

		return JsonResponse({'result': ACCEPT, 'message':r'已停止发布!'})

@csrf_exempt
def get_sorted_questionnaires(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		username = request.session.get('user')
		l = [x for x in Questionnaire.objects.filter(own = username)]
		data_json = json.loads(request.body)
		sort_method = data_json['sort_method']
		res_tmp=[]
		if sort_method == 'create_time_ascend': # 创建时间升序
			l.sort(key = lambda x: x.id)
			for x in l:
				info = Info.objects.get(id = x.id)
				if info.status == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'status':info.status,
					'create_time':x.create_time, 'upload_time':info.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'create_time_descend': # 创建时间降序
			l.sort(key = lambda x: x.id, reverse = True)
			for x in l:
				info = Info.objects.get(id = x.id)
				if info.status == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'status':info.status,
					'create_time':x.create_time, 'upload_time':info.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'upload_time_ascend': # 发布时间升序
			tmp_list = []
			for x in l:
				info = Info.objects.get(id = x.id)
				tmp_list.append(info)
			tmp_list.sort(key = lambda x: x.upload_time)
			for x in tmp_list:
				questionnaire = Questionnaire.objects.get(id = x.id)
				if x.status == DELETED:
					continue
				d = {'id':x.id, 'title':questionnaire.title, 'description':questionnaire.description, 
					'type':questionnaire.type, 'count':questionnaire.count, 'hash':questionnaire.hash, 
					'status':x.status, 'create_time':questionnaire.create_time, 'upload_time':x.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'upload_time_descend': # 发布时间降序
			tmp_list = []
			for x in l:
				info = Info.objects.get(id = x.id)
				tmp_list.append(info)
			tmp_list.sort(key = lambda x: x.upload_time, reverse = True)
			for x in tmp_list:
				questionnaire = Questionnaire.objects.get(id = x.id)
				if x.status == DELETED:
					continue
				d = {'id':x.id, 'title':questionnaire.title, 'description':questionnaire.description, 
					'type':questionnaire.type, 'count':questionnaire.count, 'hash':questionnaire.hash, 
					'status':x.status, 'create_time':questionnaire.create_time, 'upload_time':x.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'count_ascend': # 回收量升序
			l.sort(key = lambda x: x.count)
			for x in l:
				info = Info.objects.get(id = x.id)
				if info.status == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'status':info.status,
					'create_time':x.create_time, 'upload_time':info.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'count_descend': # 回收量降序
				l.sort(key = lambda x: x.count, reverse = True)
				for x in l:
					info = Info.objects.get(id = x.id)
					if info.status == DELETED:
						continue
					d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
						'count':x.count, 'hash':x.hash, 'status':info.status,
						'create_time':x.create_time, 'upload_time':info.upload_time}
					res_tmp.append(d)
				return JsonResponse({'result': ACCEPT, 'message': res_tmp})

@csrf_exempt
def search_questionnaires(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
		
		username = request.session.get('user')
		data_json = json.loads(request.body)
		
		q = data_json['query']

		res_tmp=[]

		if not q.isdigit(): # 不含数字，查标题
			l = [x for x in Questionnaire.objects.filter(Q(own = username) & Q(title = q))]
		else: # 仅数字
			l = [x for x in Questionnaire.objects.filter(Q(own = username) & Q(title = q))]
			l.extend([x for x in Questionnaire.objects.filter(Q(own = username) & Q(id = int(q)))])
		l.sort(key = lambda x: x.id)
		for x in l:
			info = Info.objects.get(id = x.id)
			if info.status == DELETED:
				continue
			d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
				'count':x.count, 'hash':x.hash, 'status':info.status,
				'create_time':x.create_time, 'upload_time':info.upload_time}
			res_tmp.append(d)
		return JsonResponse({'result': ACCEPT, 'message': res_tmp})