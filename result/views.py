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
from django.http import FileResponse
from django.http import HttpResponse
import datetime
import json
import xlrd
import xlwt
from six import BytesIO
# Create your views here.

@csrf_exempt
def submit(request):
	if request.method == 'POST':
		data_json = json.loads(request.body)
		qid = int(data_json['qid'])
		q = Questionnaire.objects.get(id = qid)
		q.count = q.count + 1
		q.save()
		results = data_json['results']
		total = SubmitInfo.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 0
		else:
			total = int(total['id__max']) + 1
		
		submitinfo = SubmitInfo(id = total, qid = qid, submit_time = str(datetime.datetime.now()))
		submitinfo.save()
		for i in results:
			submit = Submit(sid = total, problem_id = int(i['problem_id']), type = int(i['type']), answer = "")
			if i['type'] in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				ans = list_to_string(i['answer'])
			else:
				ans = i['answer'][0]
			submit.answer = ans
			submit.save()
		
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
			sh.write(i+1, 1, submits[i].submit_time[:19])
			for j in range(len(answers)):
				s = string_to_list(answers[j].answer)
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

'''
# 复制过去的答卷的提交时间早于新问卷的创建时间会不会有问题？
def copy_result(dest_qid, src_qid):
	results = SubmitInfo.objects.get(qid = src_qid)
	for x in results:
		submits = Submit.objects.filter(sid = x.id)
		submits.sort(key = lambda x: x.problem_id)
		# problem_id实际与rank同序
		questions = [x for x in Question.objects.filter(questionnaire_id = dest_qid)]
		questions.sort(key = lambda x: x.rank)

		total = SubmitInfo.objects.all().aggregate(Max('id'))
		if total['id__max'] == None:
			total = 0
		else:
			total = int(total['id__max']) + 1
		submit_info = SubmitInfo(id = total, qid = dest_qid, submit_time = x.submit_time, author = x.author)
		submit_info.save()

		num = 0
		for y in submits:
			submit = Submit(sid = submit_info.id, problem_id = questions[num].id, type = y.type, answer = y.answer)
			submit.save()
			num += 1
'''

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
				result['questions'].append({'content': q.content,
											'type': q.type, 
											'option': string_to_list(q.option),
											'count':[0]*len(string_to_list(q.option))})
			else:
				result['questions'].append({'content': q.content, 'type': q.type})
		# Put basic question informations

		for i in range(len(questions)):
			if questions[i].type not in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				answers = [x.answer for x in Submit.objects.filter(problem_id = questions[i].id)]
				s = " ".join(answers)
				# result['questions'][i]['url'] = draw_wordcloud(s)
				a,b = word_count(s)
				result['questions'][i]['option'] = a
				result['questions'][i]['count'] = b
			else:
				all = [x for x in Submit.objects.filter(problem_id = questions[i].id)]
				for x in all:
					s = string_to_list(x.answer)
					if len(s) == 0 or s[0] == '':
						continue
					s = [int(op) for op in s]
					for op in s:
						result['questions'][i]['count'][op] +=1
		return JsonResponse(result)

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