from django.http import JsonResponse
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from result.models import *
from QPlanet.values import *
from question.models import *
from questionnaire.models import *
from question.views import *
from .wordclound import *
from .verify import *
from django.http import FileResponse
from django.http import HttpResponse
from datetime import datetime
import json
import xlrd
import xlwt
from six import BytesIO
import re

@csrf_exempt
def send_captcha(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		phone = str(data_json['phone'])
		pattern = re.compile(r'^1(3\d|4[5-9]|5[0-35-9]|6[2567]|7[0-8]|8\d|9[0-35-9])\d{8}$')
		if pattern.search(phone) == None:
			return JsonResponse({'result': ERROR, 'message': r'手机号格式非法!'})
		captcha = str(send_code(phone))
		p = Phone(phone_number = phone, captcha = captcha)
		p.save()
		return JsonResponse({'result': ACCEPT, 'message': r'发送成功!'})

@csrf_exempt
def check_captcha(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		phone = str(data_json['phone'])
		captcha = data_json['captcha']
		if Phone.objects.filter(phone_number = phone, captcha = captcha).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'验证码输入错误!'})
		p = Phone.objects.get(phone_number = phone, captcha = captcha)
		p.delete()
		return JsonResponse({'result': ACCEPT, 'message': r'验证成功!'})

@csrf_exempt
def submit(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = int(data_json['qid'])
		email = data_json.get('email', '')
		phone = str(data_json.get('phone', ''))
		q = Questionnaire.objects.get(id = qid)
		author = ""
		if request.session.get('is_login') == True and q.certification == EMAIL_ADRESS:
			if SubmitInfo.objects.filter(author = request.session.get('user'), qid = q.id).exists() == True:
				return JsonResponse({'result': ERROR, 'message':r'您已填写过该问卷!'})
			author = request.session.get('user')
		elif phone != '':
			if Phone.objects.filter(phone_number = phone, qid = q.id):
				return JsonResponse({'result': ERROR, 'message':r'您已填写过该问卷!'})
		# 身份认证模块

		results = data_json['results']
		for i in results:
			question = Question.objects.get(id = i['problem_id'])
			if question.type != COMPLETION:
				continue
			lower,upper,requirement = string_to_int(question.extra)
			ans = i['answer'][0]
			if question.is_required == False and len(ans) == 0:
				continue
			if len(ans)<lower or len(ans)>upper:
				return JsonResponse({'result': ERROR, 'message':r'填空题长度非法!'})
			if requirement == PHONE_NUM:
				pattern = re.compile(r'^1(3\d|4[5-9]|5[0-35-9]|6[2567]|7[0-8]|8\d|9[0-35-9])\d{8}$')
				if pattern.search(phone) == None:
					return JsonResponse({'result': ERROR, 'message': r'手机号格式非法!'})
			if requirement == EMAIL_ADRESS:
				if '@' not in ans:
					return JsonResponse({'result': ERROR, 'message': r'邮箱格式非法!'})
			if requirement == NUMBER_ONLY:
				try:
					a = int(ans)
				except:
					return JsonResponse({'result': ERROR, 'message': r'数字格式非法!'})
		# 填空题合法性检测

		if q.type == SIGNUP:
			for i in results:
				question = Question.objects.get(id = i['problem_id'])
				option,quota = string_to_list(question.extra)
				if quota.count(-1) == len(option):
					continue
				res = count_surplus(question.id)
				ans = answer_to_string(i['answer'])
				ans = [int(x) for x in ans]
				for x in ans:
					if res[x] <= 0:
						return JsonResponse({'result': ERROR, 'message': r'容量不足!'})
		# 报名题容量检测

		q.count = q.count + 1
		q.save()
		total = SubmitInfo.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 0
		else:
			total = int(total['id__max']) + 1
		
		submitinfo = SubmitInfo.objects.create(id = total, qid = qid, author = author)
		if phone != '':
			p = Phone(phone_number = phone, captcha = "", sid = submitinfo.id, qid = q.id)
			p.save()
		for i in results:
			submit = Submit(sid = total, problem_id = int(i['problem_id']), type = int(i['type']), answer = "")
			if i['type'] in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				ans = answer_to_string(i['answer'])
			else:
				ans = i['answer'][0]
			submit.answer = ans
			submit.save()
		# 问卷记录提交

		if q.type in [TESTING_SCORE, TESTING_CORRECTION, TESTING_BOTH, TESTING_NO]:
			score = 0.
			std_ans = []
			for i in results:
				question = Question.objects.get(id = i['problem_id'])
				if question.is_essential == True:
					continue
				# 基础问题不改分

				if i['type'] in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
					ans = i['answer']
					stand = StandardAnswer.objects.get(qid = i['problem_id'])
					std_ans.append({'problem_id': i['problem_id'],
							'ans': [int (x) for x in string_to_answer(stand.content)],
							'type':question.type,
							'score':stand.score,
							'content':question.content}
					)
					# 预处理与标准答案
					if i['type'] == SINGLE_CHOICE:
						if str(ans[0]) == stand.content:
							score += stand.score
						# 单选得分
					else:
						ans = [int(x) for x in ans]
						ans.sort()
						std = string_to_answer(stand.content)
						std = [int(x) for x in std]
						std.sort()
						if ans == std:
							score += stand.score
						elif q.select_less_score == True:
							count = sum([1 if x in std else 0 for x in ans])
							if count == len(ans) and len(ans)>=1:
								score += stand.score/2
						# 多选得分
				else:
					ans = i['answer'][0]
					stand = StandardAnswer.objects.get(qid = i['problem_id'])
					std = string_to_answer(stand.content)
					std_ans.append({'problem_id': i['problem_id'],
							'ans': std,
							'type':question.type,
							'score':stand.score,
							'content':question.content}
					)
					if ans in std:
						score += stand.score
					# 填空得分
			
			submitinfo.score = score
			submitinfo.save()
			# 改卷部分

			if q.type == TESTING_NO:
				return JsonResponse({'result': ACCEPT, 'message': r'提交成功!'})
			js = {'result': ACCEPT, 'message': r'提交成功!'}
			if q.type in [TESTING_SCORE, TESTING_BOTH]:
				js['score'] = score
			if q.type in [TESTING_BOTH, TESTING_CORRECTION]:
				js['stand_ans'] = std_ans
			return JsonResponse(js)
			# 反馈部分
		elif q.type in [VOTING_AFTER, VOTING_BOTH]:
			js = {'result': ACCEPT, 'message': r'提交成功!'}
			js['votes'] = []
			for i in results:
				question = Question.objects.get(id = i['problem_id'])
				if question.is_essential == True:
					continue
				if question.type not in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
					continue
				votes = count_submissions(question.id)
				js['votes'].append({'problem_id': question.id, 'result': votes})
			return JsonResponse(js)
			# 投票
		return JsonResponse({'result': ACCEPT, 'message': r'提交成功!'})

def delete_result(qid):
	results = SubmitInfo.objects.filter(qid = qid)
	for x in results:
		Submit.objects.filter(sid = x.id).delete()
		x.delete()

@csrf_exempt
def download(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		hash = data_json['hash']
		if Questionnaire.objects.filter(hash = hash).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'问卷不存在!'})
		q = Questionnaire.objects.get(hash = hash)
		qid = q.id
		book = xlwt.Workbook(encoding = 'ascii')
		sh = book.add_sheet('Sheet1')
		
		submits = [x for x in SubmitInfo.objects.filter(qid = qid)]
		submits.sort(key = lambda x: x.submit_time)
		for i in range(len(submits)):
			answers = [x for x in Submit.objects.filter(sid = submits[i].id)]
			answers.sort(key = lambda x: x.problem_id)
			if i == 0:
				sh.write(0, 0, r'提交ID')
				sh.write(0, 1, r'提交时间')
				for j in range(len(answers)):
					p = Question.objects.get(id = answers[j].problem_id)
					sh.write(0, j+2, p.content)
				# Print the title
			sh.write(i+1, 0, i)
			sh.write(i+1, 1, submits[i].submit_time.strftime('%Y-%m-%d %H:%M:%S'))
			for j in range(len(answers)):
				s = string_to_list(answers[j].answer)
				if len(s) == 0 or s[0] == "":
					continue
				if answers[j].type == SINGLE_CHOICE:
					ans = chr(int(s[0]) + 65)
				elif answers[j].type == MULTIPLE_CHOICE:
					s = [chr(int(x) + 65) for x in s]
					ans = ','.join(s)
				else:
					ans = s[0]
				sh.write(i+1, j+2, ans)
		
		name = 'img/' + str(qid) + '.xls'
		book.save(name)
		return JsonResponse({'result': ACCEPT, 'message': r'成功!', 'name':str(qid) + '.xls'})

@csrf_exempt
def analyze(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		hash = data_json['hash']
		if Questionnaire.objects.filter(hash = hash).exists() == False:
			return JsonResponse({'result': ERROR, 'message': r'问卷不存在!'})
		q = Questionnaire.objects.get(hash = hash)
		qid = q.id
		result = {'qid': qid}
		
		infos = [x for x in SubmitInfo.objects.filter(qid = qid)]
		
		result['result'] = ACCEPT
		result['message'] = r'获取成功!'
		result['total'] = len(infos)
		result['questions'] = []
		
		questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
		questions.sort(key = lambda x : x.rank)
		for q in questions:
			if q.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				op,fk = string_to_list(q.extra)
				result['questions'].append({'id': q.id,
											'content': q.content,
											'type': q.type, 
											'option': op,
											'count':[0]*len(op)})
			elif q.type in [COMPLETION, DESCRIPTION]:
				result['questions'].append({'content': q.content, 'type': q.type})
			elif q.type == GRADING:
				lower,upper,bin = string_to_int(q.extra)
				result['questions'].append({'id': q.id,
											'content': q.content,
											'type': q.type, 
											'option': [i for i in range(1,upper+1)],
											'count':[0]*upper})
			else:
				pass
				# TODO analyze locations
		# Put basic question informations

		for i in range(len(questions)):
			if questions[i].type in [COMPLETION, DESCRIPTION]:
				answers = [x.answer for x in Submit.objects.filter(problem_id = questions[i].id)]
				submit_id = [x.sid for x in Submit.objects.filter(problem_id = questions[i].id)]
				submit_time = []
				for x in submit_id:
					info = SubmitInfo.objects.get(id = x, qid = qid)
					submit_time.append(str(info.submit_time)[:16])
				s = " ".join(answers)
				# result['questions'][i]['url'] = draw_wordcloud(s)
				a,b = word_count(s)
				result['questions'][i]['option'] = a
				result['questions'][i]['count'] = b
				result['questions'][i]['all'] = answers
				result['questions'][i]['submit_time'] = submit_time
			else:
				all = [x for x in Submit.objects.filter(problem_id = questions[i].id)]
				for x in all:
					s = string_to_answer(x.answer)
					if len(s) == 0 or s[0] == '':
						continue
					s = [int(op) for op in s]
					if questions[i].type == GRADING:
						s = [i-1 for i in s]
					# 打分题从1开始,其他选择从0开始
					# 减去偏移量

					for op in s:
						result['questions'][i]['count'][op] +=1
		return JsonResponse(result)

@csrf_exempt
def cross_analyze(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = int(data_json['qid'])
		t1 = int(data_json['t1'])
		t2 = int(data_json['t2'])
		q1 = Question.objects.get(id = t1)
		q2 = Question.objects.get(id = t2)
		if q1.type not in [SINGLE_CHOICE, MULTIPLE_CHOICE] and q2.type not in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
			return JsonResponse({'result': ERROR, 'message':r'请重新选择题目!'})
		
		option,quota = string_to_list(q1.extra)
		len1 = len(option)
		option,quota = string_to_list(q2.extra)
		len2 = len(option)

		count = [[0 for i in range(len2)] for i in range(len1)]
		submitinfo = [x for x in SubmitInfo.objects.filter(qid = qid)]
		total = len(submitinfo)
		
		for x in submitinfo:
			s1 = Submit.objects.get(sid = x.id, problem_id = q1.id)
			s2 = Submit.objects.get(sid = x.id, problem_id = q2.id)
			ans1 = [int(x) for x in string_to_answer(s1.answer)]
			ans2 = [int(x) for x in string_to_answer(s2.answer)]
			for i in ans1:
				for j in ans2:
					count[i][j] += 1
		js = {'result': ACCEPT, 'message': r'成功!'}
		js['total'] = total
		js['count'] = count
		return JsonResponse(js)

		# Some calculations
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