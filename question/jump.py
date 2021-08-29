from question.models import *
from question.views import *
from QPlanet.values import *

def answer_to_string(answer):
	answer = [str(x) for x in answer]
	return SEPARATOR.join(answer)

def string_to_answer(answer):
	return list(answer.split(SEPARATOR))

def load_jump(id):
	if Jump.objects.filter(qid = id).exists() == False:
		return {'nextProblem': [-1]}
	jump = Jump.objects.get(qid = id)
	d = {}
	d['nextProblem'] = string_to_answer(jump.next)
	return d
# 获取一个题目的跳题

def save_jump(questions):
	for i in questions:
		if Jump.objects.filter(qid = int(i['qid'])).exists() == True:
			jump = Jump.objects.get(id = int(i['qid']))
			jump.delete()
		next = i['logic']['nextProblems']
		jump = Jump(qid = int(i['qid']), next = answer_to_string(next))
		jump.save()
# 储存一个问卷的所有跳题
