from questionnaire.models import Questionnaire
from django.shortcuts import render
from question.models import *
from django.views.decorators.csrf import csrf_exempt
from QPlanet.values import *
from QPlanet.settings import *
from result.models import *
from django.http import JsonResponse
import json

def list_to_string(option, quota):
    return SEPARATOR.join(option + list(map(str, quota)))

def string_to_list(extra):
    tmp = list(extra.split(SEPARATOR))
    option = tmp[: len(tmp) // 2]
    quota = tmp[len(tmp) // 2: ]
    return option, list(map(int, quota))

def int_to_string(lower, upper, requirement):
    return SEPARATOR.join([str(lower), str(upper), str(requirement)])

def string_to_int(extra):
    return list(map(int, extra.split(SEPARATOR)))

def answer_to_string(answer):
    answer = [str(x) for x in answer]
    return SEPARATOR.join(answer)

def string_to_answer(answer):
    return list(answer.split(SEPARATOR))

def count_submissions(pid):
    question = Question.objects.get(id = pid)
    option,quota = string_to_list(question.extra)
    count = [0 for i in range(len(option))]
    all = [x for x in Submit.objects.filter(problem_id = question.id)]
    count = 0
    for i in all:
        ans = [int(x) for x in answer_to_string(i.answer)]
        for j in ans:
            count[j] += 1
	return count

def count_surplus(question_id):
    question = Question.objects.get(id = question_id)
    res = string_to_list(question.extra)
    quota = res[1]
    len = quota.length()
    res = []
    submission = count_submissions(question_id)
    for i in range(len):
        res[i] = quota[i] - submission[i]
    return res

@csrf_exempt
def surplus_quota(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        qid = int(data_json['qid'])
        return JsonResponse({'result': ACCEPT, 'surplus': count_surplus(qid)})

def save_questions(questions, qid):
    if questions:
        num = 1
        for x in questions:
            question = Question(
                questionnaire_id = qid, rank = num, type = x['type'], content = x['content'], 
                is_required = x['is_required'], is_essential = x.get('is_essential', False),
                description = x.get('description', None)
            )
            if x['type'] in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
                question.extra = list_to_string(x['option'], x['quota'])
            elif x['type'] in [COMPLETION, DESCRIPTION]:
                question.extra = int_to_string(x['lower'], x['upper'], x['requirement'])
            elif x['type'] == GRADING:
                question.extra = int_to_string(0, x['upper'], 0)
            question.save()
            if x.get('standard_answer', -1) != -1 and x['standard_answer']['score'] != -1:  # for copy
                tmp = x.get('standard_answer')
                question_id = Question.objects.get(questionnaire_id = qid, rank = num)
                question_id = question_id.id
                std = StandardAnswer(qid = question_id, type = x['type'], content = answer_to_string(tmp['content']), score = int(tmp['score']))
                std.save()
            num += 1

def delete_questions(qid):
    questions = Question.objects.filter(questionnaire_id = qid)
    for question in questions:
        StandardAnswer.objects.filter(qid = question.id).delete()
        question.delete()

def get_questions(qid, with_id = True):
    questionnaire = Questionnaire.objects.get(id = qid)
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        d = {'type': x.type, 'content': x.content, 'is_required': x.is_required, 
            'is_essential': x.is_essential, 'description': x.description}
        if with_id:
            d['id'] = x.id
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            res = string_to_list(x.extra)
            d['option'] = res[0]
            d['quota'] = res[1]
            d['lower'] = -1
            d['upper'] = -1
            d['requirement'] = -1
            if questionnaire.type in [1, 2, 3, 4] and res[1][0] > 0:
                d['surplus'] = count_surplus(x.id)
        elif x.type in [COMPLETION, DESCRIPTION, GRADING]:
            res = string_to_int(x.extra)
            d['option'] = []
            d['quota'] = []
            d['lower'] = res[0]
            d['upper'] = res[1]
            d['requirement'] = res[2]
        elif x.type == GRADING:
            d['option'] = []
            d['quota'] = []
            d['lower'] = -1
            d['upper'] = -1
            d['requirement'] = -1
        if StandardAnswer.objects.filter(qid = x.id).exists():
            standard_answer = StandardAnswer.objects.get(qid = x.id)
            d['standard_answer'] = {'content': string_to_answer(standard_answer.content), 
                'score': standard_answer.score}
            if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
                d['standard_answer']['content'] = [int(x) for x in d['standard_answer']['content']]
        else:
            d['standard_answer'] = {'content': [], 'score': -1}
        tmp.append(d)
    return tmp

def update_questions(questions):
    num = 1
    for x in questions:
        question = Question.objects.get(id = x['id'])
        question.content= x['content']
        question.is_required = x['is_required']
        if x.get('is_essential', -1) != -1:
            question.is_essential = x['is_essential']
        if x.get('description', -1) != -1:
            question.description = x['description']
        question.rank = num
        if question.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            question.extra = list_to_string(x['option'], x['quota'])
        elif question.type in [COMPLETION, DESCRIPTION]:
            question.extra = int_to_string(x['lower'], x['upper'], x['requirement'])
        elif question.type == GRADING:
            question.extra = int_to_string(0, x['upper'], 0)
        question.save()
        num += 1