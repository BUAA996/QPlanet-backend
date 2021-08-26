from questionnaire.models import Questionnaire
from django.shortcuts import render
from question.models import *
from django.views.decorators.csrf import csrf_exempt
from QPlanet.values import *
from QPlanet.settings import *
#from questionnaire.views import *
# Create your views here.

def list_to_string(option, quota):
    return SEPARATOR.join(option + list(map(str, quota)))

def string_to_list(extra):
    tmp = list(extra.split(SEPARATOR))
    option = tmp[: len(tmp) // 2 + 1]
    quota = tmp[len(tmp) // 2 + 1: ]
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
            question.save()
            if question.get('standard_answer', -1) != -1:
                tmp = question.get('standard_answer')
                question_id = Question.objects.filter(questionnaire_id = qid, rank = num)
                StandardAnswer.objects.create(qid = question_id, type = x['type'], score = tmp['score'],
                    content = answer_to_string(tmp['content']))
            num += 1

def delete_question(qid):
    Question.objects.filter(questionnaire_id = qid).delete()
    

def get_questions(qid):
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]: 
            d = {'id':x.id, 'type':x.type, 'content':x.content, 'option':string_to_list(x.option),
                'is_required':x.is_required, 'description':x.description }
        else:
            d = {'id':x.id, 'type':x.type, 'content':x.content, 'is_required':x.is_required,
                'description':x.description }
        tmp.append(d)
    return tmp

def get_questions_without_id(qid):
    questions = [x for x in Question.objects.filter(questionnaire_id = qid)]
    questions.sort(key = lambda x: x.rank)
    tmp = []
    for x in questions:
        if x.type in [SINGLE_CHOICE, MULTIPLE_CHOICE]: 
            d = {'type':x.type, 'content':x.content, 'option':string_to_list(x.option),
                'is_required':x.is_required, 'description':x.description }
        else:
            d = {'type':x.type, 'content':x.content, 'is_required':x.is_required,
                'description':x.description }
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
        if type in [SINGLE_CHOICE, MULTIPLE_CHOICE]:
            question.option = list_to_string(x['option'])
        question.save()
        num += 1