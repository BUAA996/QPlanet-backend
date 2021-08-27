from result.views import delete_result
from django.http import JsonResponse
from django.shortcuts import render
from questionnaire.models import *
from user.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max, query_utils
from django.utils import timezone
from QPlanet.values import *
from QPlanet.settings import *
from question.views import *
from result.views import *
import qrcode
import json
from datetime import datetime, timedelta
import random
import string
from django import utils
from django.db.models import Q
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt,RGBColor
from docx2pdf import convert
from random import randint as rand

def datetime_to_str(time):
	return time.strftime('%Y-%m-%d %H:%M')

def check_close(q):
	#TODO calculate the res
	info = Info.objects.get(id = q.id)
	if info.state != RELEASE:
		return 0
	if datetime.now() < q.deadline:
		return 0
	info.state = CLOSED
	info.save()
	return 1

def hash(id):
	q = Questionnaire.objects.get(id = id)
	q.hash = ''.join(random.sample(string.ascii_letters + string.digits, 7)) + str(q.type)
	q.save()
	return q.hash

def build_questionnaire(title, description, own, type, deadline, duration, random_order, select_less_score, certification, show_number, questions):
	total = Questionnaire.objects.all().aggregate(Max('id'))
	if total['id__max'] == None:
		total = 1
	else:
		total = int(total['id__max']) + 1
		
	questionnaire = Questionnaire.objects.create(
		id = total, title = title, description = description, own = own, type = type, deadline = deadline, 
		duration = duration, count = 0, hash = hash(total), random_order = random_order, 
		select_less_score = select_less_score, certification = certification, show_number = show_number)

	save_questions(questions, questionnaire.id)
	Info.objects.create(id = total, state = SAVED)
	return [questionnaire.id, questionnaire.hash]

@csrf_exempt
def create(request):
	if request.method == 'POST':
		if request.session.get('is_login') != True:
			return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})

		data_json = json.loads(request.body)
		username = request.session.get('user')

		res = build_questionnaire(title = data_json['title'],
					description = data_json['description'],
					own = username,
					type = int(data_json['type']),
					deadline = data_json.get('deadline', datetime.now() + timedelta(hours = 72)),
					# TODO DDL 默认时间设置问题
					duration = int(data_json.get('duration', 0)),
					random_order = data_json.get('random_order', False),
					select_less_score = data_json.get('select_less_score', False),
					certification = data_json['certification'],
					show_number = data_json.get('show_number', True),
					questions = data_json['questions']
			)
		return JsonResponse({'result': ACCEPT, 'message': r'保存成功!', 'id': res[0], 'hash': res[1]})

		'''
		if data_json.get('title', -1) != -1 and data_json.get('description', -1) != -1 \
			and data_json.get('type', -1) != -1 and data_json.get('limit_time', -1) != -1 \
			and data_json.get('questions', -1) != -1 :
			for x in data_json['questions']:
				if x.get('type', -1) == -1 or x.get('content', -1) == -1 or x.get('is_required', -1) == -1 \
					or x.get('description', -1) == -1:
					return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
				if (x.get('type') in [SINGLE_CHOICE, MULTIPLE_CHOICE] and x.get('option', -1) == -1) \
					or (x.get('type') not in [SINGLE_CHOICE, MULTIPLE_CHOICE] and x.get('option', -1) != -1):
					return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
		else:
			return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
		'''

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
			check_close(x)
			info = Info.objects.get(id = x.id)
			d = {'id': x.id, 'title': x.title, 'description': x.description, 'type': x.type,
				'count': x.count, 'hash': x.hash, 'state': info.state, 'quota': x.quota, 
				'create_time': datetime_to_str(x.create_time), 
				'upload_time': datetime_to_str(info.upload_time)
			}
			dt_time = x.create_time.strftime('%Y-%m-%d %H:%M:%S')
			d['create_time_int'] = int(dt_time.timestamp())
			dt_time = x.upload_time.strftime('%Y-%m-%d %H:%M:%S')
			d['upload_time_int'] = int(dt_time.timestamp())
			result['questionnaires'].append(d)
		return JsonResponse(result)

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
		if q.state == DELETED:
			questionnaire = Questionnaire.objects.get(id = q.id)
			delete_questions(id)
			delete_result(id)
			questionnaire.delete()
			q.delete()
			return JsonResponse({'result': ACCEPT, 'message':r'已彻底删除该问卷!'})
		else:
			q.state = DELETED
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
		q.state = SAVED
		q.save()
		return JsonResponse({'result': ACCEPT, 'message':r'已恢复!'})

@csrf_exempt
def release(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		id = int(data_json['id'])

		info = Info.objects.get(id = id)
		info.state = RELEASE
		info.save()

		_hash = hash(id)
		url = IMG_URL + _hash
		pic = qrcode.make(url)
		with open("img/"+_hash +".png","wb") as f:
			pic.save(f)
		return JsonResponse({'result': ACCEPT, 'message': r'发布成功!', 'url': url, 'img': IMG_URL + 'img/' + _hash + '.png'})

@csrf_exempt
def get_qr(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		id = int(data_json['id'])
		q = Questionnaire.objects.get(id = id)
		return JsonResponse({'result': ACCEPT, 'message':r'获取成功!', 'img':IMG_URL + 'img/' + q.hash + '.png'})

@csrf_exempt
def close(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		id = int(data_json['id'])

		info = Info.objects.get(id = id)
		info.state = SAVED
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
				if info.state == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'state':info.state,
					'create_time':x.create_time[:16], 'upload_time':info.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'create_time_descend': # 创建时间降序
			l.sort(key = lambda x: x.id, reverse = True)
			for x in l:
				info = Info.objects.get(id = x.id)
				if info.state == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'state':info.state,
					'create_time':x.create_time[:16], 'upload_time':info.upload_time}
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
				if x.state == DELETED:
					continue
				d = {'id':x.id, 'title':questionnaire.title, 'description':questionnaire.description, 
					'type':questionnaire.type, 'count':questionnaire.count, 'hash':questionnaire.hash, 
					'state':x.state, 'create_time':questionnaire.create_time[:16], 'upload_time':x.upload_time}
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
				if x.state == DELETED:
					continue
				d = {'id':x.id, 'title':questionnaire.title, 'description':questionnaire.description, 
					'type':questionnaire.type, 'count':questionnaire.count, 'hash':questionnaire.hash, 
					'state':x.state, 'create_time':questionnaire.create_time[:16], 'upload_time':x.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'count_ascend': # 回收量升序
			l.sort(key = lambda x: x.count)
			for x in l:
				info = Info.objects.get(id = x.id)
				if info.state == DELETED:
					continue
				d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
					'count':x.count, 'hash':x.hash, 'state':info.state,
					'create_time':x.create_time[:16], 'upload_time':info.upload_time}
				res_tmp.append(d)
			return JsonResponse({'result': ACCEPT, 'message': res_tmp})
		elif sort_method == 'count_descend': # 回收量降序
				l.sort(key = lambda x: x.count, reverse = True)
				for x in l:
					info = Info.objects.get(id = x.id)
					if info.state == DELETED:
						continue
					d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
						'count':x.count, 'hash':x.hash, 'state':info.state,
						'create_time':x.create_time[:16], 'upload_time':info.upload_time}
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

		res_tmp = []

		if not q.isdigit(): # 非仅数字，查标题
			l = [x for x in Questionnaire.objects.filter(Q(own = username) & Q(title__icontains = q))]
		else: # 仅数字
			l = [x for x in Questionnaire.objects.filter(Q(own = username) & Q(title__icontains = q))]
			l.extend([x for x in Questionnaire.objects.filter(Q(own = username) & Q(id = int(q)))])
		l.sort(key = lambda x: x.id)
		for x in l:
			info = Info.objects.get(id = x.id)
			d = {'id':x.id, 'title':x.title, 'description':x.description, 'type':x.type,
				'count':x.count, 'hash':x.hash, 'state':info.state,
				'create_time':x.create_time[:16], 'upload_time':info.upload_time}
			dt_time = datetime.datetime.strptime(x.create_time[:19], '%Y-%m-%d %H:%M:%S')
			d['create_time_int'] = int(dt_time.timestamp())
			d['upload_time_int'] = 0
			if info.upload_time != "":
				dt_time = datetime.datetime.strptime(info.upload_time[:19], '%Y-%m-%d %H:%M:%S')
				d['upload_time_int'] = int(dt_time.timestamp())
				d['upload_time'] = d['upload_time'][:16]
			res_tmp.append(d)
		return JsonResponse({'result': ACCEPT, 'message': res_tmp})

@csrf_exempt
def check_type(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		hash = data_json['hash']
		if Questionnaire.objects.filter(hash = hash).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'问卷不存在!'})
		else:
			q = Questionnaire.objects.get(hash = hash)
			if check_close(q) == 1:
				return JsonResponse({'result': ERROR, 'message':r'问卷已关闭!'})
			return JsonResponse({'result': ACCEPT, 'message': r'获取成功!', 'requirement': int(hash[-1])})

@csrf_exempt
def view(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		if data_json.get('qid', -1) != -1:
			qid = int(data_json['qid'])
			if request.session.get('is_login') != True:
				return JsonResponse({'result': ERROR, 'message': r'您还未登录!'})
			q = Questionnaire.objects.get(id = qid)
			if q.own != request.session.get('user'):
				return JsonResponse({'result': ERROR, 'message': r'您没有权限!'})
		else:
			hash = data_json['hash']
			if Questionnaire.objects.filter(hash=hash).exists() == False:
				return JsonResponse({'result': ERROR, 'message': r'问卷不存在!'})
			q = Questionnaire.objects.get(hash = hash)
		# if check_close(q):
		# 	 return JsonResponse({'result': ERROR, 'message': r'问卷已关闭!'})
		info = Info.objects.get(id = q.id)
		
		result = {'qid':q.id, 'title':q.title, 'description':q.description,
					'type':q.type, 'show_number': q.show_number}
		result['questions'] = get_questions(q.id)
		result['result'] = ACCEPT
		result['message'] = r'获取成功!'
		return JsonResponse(result)

@csrf_exempt
def fill(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		hash = data_json['hash']
		if Questionnaire.objects.filter(hash=hash).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'问卷不存在!'})
		q = Questionnaire.objects.get(hash = hash)
		info = Info.objects.get(id = q.id)
		check_close(q)
		if info.state != RELEASE:
			return JsonResponse({'result': ERROR, 'message': r'问卷未发布!'})
		# TODO more information
		# Vote
		# Sign
		result = {'qid':q.id, 'title':q.title, 'description':q.description, 'type':q.type}
		result['questions'] = get_questions(q.id)
		if q.random_order == True:
			a = result['questions']
			l = len(a)
			# TODO set random seed
			# random.seed(1)
			for i in range(30):
				x = rand(0, l-1)
				y = rand(0, l-1)
				if a[x].is_essential == True or a[y].is_essential == True:
					continue
				a[x],a[y] = a[y],a[x]
			result['questions'] = a
		result['result'] = ACCEPT
		result['message'] = r'获取成功!'
		return JsonResponse(result)

@csrf_exempt
def modify_questionnaire(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		
		if data_json.get('title', -1) != -1 and data_json.get('description', -1) != -1 \
			and data_json.get('modify_type', -1) != -1 and data_json.get('limit_time', -1) != -1 \
			and data_json.get('questions', -1) != -1 and data_json.get('qid', -1) != -1:
			for x in data_json['questions']:
				# 新题目 id ？
				if x.get('id', -1) == -1 or x.get('content', -1) == -1 or x.get('is_required', -1) == -1 \
					or x.get('description', -1) == -1:
					return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
				if (x.get('type') in [SINGLE_CHOICE, MULTIPLE_CHOICE] and x.get('option', -1) == -1) \
					or (x.get('type') not in [SINGLE_CHOICE, MULTIPLE_CHOICE] and x.get('option', -1) != -1):
					return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
		else:
			return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
		
		modify_type = data_json['modify_type']
		qid = data_json['qid']
		q = Questionnaire.objects.get(id = qid)
		title = data_json['title']
		description = data_json['description']
		validity = data_json['validity']
		limit_time = data_json['limit_time']
		questions = data_json['questions']
		
		q.state = SAVED
		q.title = title
		q.description = description
		q.validity = validity
		q.limit_time = limit_time
		q.save()
		
		# 方式一：保留答卷；不能加题不能删题不能转换题目类型，可以移动题目不能移动选项，非考试类型可以加选项
		if modify_type == 'reserve_results':
			update_questions(questions) # TODO
		# 方式二：删除所有答卷（题目删掉重写）；
		elif modify_type == 'delete_all_results':
			delete_questions(qid)
			save_questions(questions, qid)
			q.count = 0
			q.save()
			delete_result(qid)
		else:
			return JsonResponse({'result': ERROR, 'message': FORM_ERROR})
		return JsonResponse({'result': ACCEPT})

def copy_questionnaire(qid, title, to_username):
	q = Questionnaire.objects.get(id = qid)
	questions = get_questions(qid, False)
	res = build_questionnaire(title, q.description, q.type, q.limit_time, q.validity, to_username, questions)
	return res

@csrf_exempt
def copy_questionnaire_to_self(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = data_json['qid']
		title = data_json['title']
		username = request.session.get('user')
		res = copy_questionnaire(qid, title, username)
		result = {'result': ACCEPT, 'copy_id': res[0], 'copy_hash': res[1]}
		return JsonResponse(result)

@csrf_exempt
def download(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		if data_json.get('id', -1) != -1:
			id = int(data_json['id'])
			q = Questionnaire.objects.get(id = id)
		else:
			hash = data_json['hash']
			q = Questionnaire.objects.get(hash = hash)
		problems = [x for x in Question.objects.filter(questionnaire_id = q.id)]
		name = str(q.id)

		document = Document()
		Head = document.add_heading("",level=1)
		run  = Head.add_run(q.title)
		run.font.name=u'Cambria'
		run._element.rPr.rFonts.set(qn('w:eastAsia'), u'Cambria')
		run.font.color.rgb = RGBColor(0,0,0)
		
		paragraph = document.add_paragraph("\n")
		count = 1
		for x in problems:
			if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				s = str(count) + "."
				if x.type == SINGLE_CHOICE:
					s += r'(单选) '
				else:
					s += r'(多选) '
				paragraph = document.add_paragraph(s + x.content)
				options = string_to_list(x.option)
				for j in range(len(options)):
					s = chr(j + 65) + '. '
					s = s + options[j]
					paragraph = document.add_paragraph(s)
				paragraph = document.add_paragraph("\n")
			elif x.type in [COMPLETION, DESCRIPTION]:
				if x.type == COMPLETION:
					s = str(count) + r".(填空) "
				else:
					s = str(count) + r".(简答) "
				paragraph = document.add_paragraph(s + x.content)
				paragraph = document.add_paragraph(r'___________________')
				if x.type == DESCRIPTION:
					paragraph = document.add_paragraph(r'___________________')
					paragraph = document.add_paragraph(r'___________________')
				paragraph = document.add_paragraph("\n")
			elif x.type == GRADING:
				s = str(count) + r".(打分) "
				# TODO add more detail
				paragraph = document.add_paragraph(s + x.content)
				paragraph = document.add_paragraph(r'___________________')
			else:
				s = str(count) + r".(定位) "
				paragraph = document.add_paragraph(s + x.content)
				paragraph = document.add_paragraph(r'___________________')
			count += 1
		
		document.save('img/' + name + '.docx')

		return JsonResponse({'result': ACCEPT, 'message':r'获取成功!', 
							'doc_name':name + '.docx', 'pdf_name':name + '.pdf'})