from django.http import JsonResponse
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from result.models import *
from QPlanet.values import *
from question.models import *
from question.views import *
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
		result = {'qid':qid}
		infos = [x for x in SubmitInfo.objects.filter(qid = qid)]
		
		result['result'] = ACCEPT
		result['message'] = r'获取成功!'
		result['total'] = len(infos)
		result['questions'] = []
		
		questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
		questions.sort(key = lambda x : x.rank)
		for q in questions:
			if q.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				result['questions'].append({'type': q.type, 
											'option': string_to_list(q.option),
											'count':[0]*len(string_to_list(q.option))})
			else:
				result['questions'].append({'type': q.type, 'url':''})
		# Put basic question informations

		for i in range(len(questions)):
			if questions[i].type not in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
				continue
				# TODO text analyze
			else:
				print(questions[i].id)
				all = [x for x in Submit.objects.filter(problem_id = questions[i].id)]
				for x in all:
					op = int(x.answer)
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