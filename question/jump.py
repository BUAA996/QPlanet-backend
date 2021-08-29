from question.models import *
from QPlanet.values import *
from questionnaire.models import *

def answer_to_string(answer):
	answer = [str(x) for x in answer]
	return SEPARATOR.join(answer)

def string_to_answer(answer):
	return list(map(int,answer.split(SEPARATOR)))

def string_to_list(extra):
	tmp = list(extra.split(SEPARATOR))
	option = tmp[: len(tmp) // 2]
	quota = tmp[len(tmp) // 2: ]
	return option, list(map(int, quota))

def load_jump(id):
	if Jump.objects.filter(qid = id).exists() == False:
		question = Question.objects.get(id = id)
		if question.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
			option,extra = string_to_list(question.extra)
			return {'nextProblem': [-1 for i in range(len(option))]}
		else:
			return {'nextProblem': [-1]}
	jump = Jump.objects.get(qid = id)
	d = {}
	d['nextProblem'] = string_to_answer(jump.next)
	return d
# 获取一个题目的跳题

def save_jump(questions):
	for i in questions:
		if Jump.objects.filter(qid = int(i['qid'])).exists() == True:
			jump = Jump.objects.get(qid = int(i['qid']))
			jump.delete()
		next = i['logic']['nextProblems']
		jump = Jump(qid = int(i['qid']), next = answer_to_string(next))
		jump.save()
	if len(questions) == 0:
		return
	q = Question.objects.get(id = questions[0]['qid'])
	q = Questionnaire.objects.get(id = q.questionnaire_id)
	q.random_order = False
# 储存一个问卷的所有跳题
