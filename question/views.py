from questionnaire.models import Questionnaire
from django.shortcuts import render
from question.models import *
from django.views.decorators.csrf import csrf_exempt
from QPlanet.values import *
from QPlanet.settings import *

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
    return SEPARATOR.join(answer)

def string_to_answer(answer):
    return answer.split(SEPARATOR)

def save_questions(questions, qid):
    if questions:
        num = 1
        for x in questions:
            question = Question(
                questionnaire_id = qid, rank = num, type = x['type'], content = x['content'], 
                is_required = x['is_required'], description = x['description']
            )
            if x['type'] in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
                question.extra = list_to_string(x['option'], x['quota'])
            elif x['type'] in [COMPLETION, DESCRIPTION]:
                question.extra = int_to_string(x['lower'], x['upper'], x['requirement'])
            elif x['type'] == GRADING:
                question.extra = int_to_string(0, x['upper'], 0)
            if x.get('is_essential', -1) != -1:
                question.is_essential = x['is_essential']
            question.save()
            if x.get('standard_answer', -1) != -1 and x['standard_answer']['score'] != -1:
                tmp = x.get('standard_answer')
                question_id = Question.objects.filter(questionnaire_id = qid, rank = num)
                StandardAnswer.objects.create(qid = question_id, type = x['type'], score = tmp['score'],
                    content = answer_to_string(tmp['content']))
            num += 1

def delete_questions(qid):
    questions = Question.objects.filter(questionnaire_id = qid)
    for question in questions:
        StandardAnswer.objects.filter(qid = question.id).delete()
    Question.objects.filter(questionnaire_id = qid).delete()

def get_questions(qid, with_id = True):
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        d = {'type': x.type, 'content': x.content, 'is_required': x.is_required, 
            'description': x.description, 'is_essential': x.is_essential}
        if with_id:
            d['id'] = x.id
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            res = string_to_list(x.extra)
            d['option'] = res[0]
            d['quota'] = res[1]
            d['lower'] = -1
            d['upper'] = -1
            d['requirement'] = -1
        elif x.type in [COMPLETION, DESCRIPTION, GRADING]:
            res = string_to_int(x.extra)
            d['option'] = []
            d['quota'] = []
            d['lower'] = res[0]
            d['upper'] = res[1]
            d['requirement'] = res[2]
        if StandardAnswer.objects.filter(qid = x.id).exists():
            standard_answer = StandardAnswer.objects.filter(qid = x.id)
            d['standard_answer'] = {'content': string_to_answer(standard_answer.content), 
                'score': standard_answer.score}
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
        question.description = x['description']
        question.rank = num
        if question.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            question.extra = list_to_string(x['option'], x['quota'])
        elif type in [COMPLETION, DESCRIPTION, GRADING]:
            question.extra = int_to_string(x['lower'], x['upper'], x['requirement'])
        question.save()
        num += 1