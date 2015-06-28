from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from tests.models import PreQuestion, Test, Answer, PostQuestion
from .const import prequestions_state


def index(requst):
    return redirect('/admin')


def test(request, test_id):
    print(dict(request.session))
    try:
        test_instance = Test.objects.get(id=test_id)

    except Exception:
        return HttpResponseNotFound('Такого теста не существует')

    # put current test id in session
    request.session['test_id'] = test_id
    request.session['state'] = prequestions_state

    # retrieve related questions and put them in session
    prequestions = PreQuestion.objects.filter(test=test_id).order_by('order')
    context = {
        'test_title': test_instance.title,
        'question_id': prequestions[0].id if len(prequestions) > 0 else 0
    }
    return render_to_response('test.html', context)


def prequestion(request, question_id):
    print(dict(request.session))
    #question_instance = PreQuestion.objects.get(id=question_id)
    test_id = request.session['test_id']
    print('d0')
    prequestions = PreQuestion.objects.filter(test=test_id).order_by('order')

    print('d1')
    if len(prequestions) == 0:
        print('d2')
        return HttpResponseNotFound('Вопросов к этому тесту не найдено')
    next_q = None
    prev_q = None
    print('d3')

    for i in range(0, len(prequestions)):
        print('d4')
        if prequestions[i].id == question_id:
            print('d5')
            question_instance = prequestions[i]
            if i != 0:
                prev_q = prequestions[i - 1].id
            if i != len(prequestions) - 1:
                next_q = prequestions[i + 1].id

            print('d6')
            context = {
                'question_title': question_instance.title,
                'answers': Answer.objects.filter(question=question_id)
            }
            print('d7')
            return render_to_response('question.html', context)

    return HttpResponseNotFound('Такого вопроса не существует')