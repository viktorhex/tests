from random import shuffle
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from tests.models import PreQuestion, Test, Answer, PostQuestion, ImagePair, Image, TrainingImagePair
from .const import prequestions_state, postquestions_state, pairs_state, initial_state, training_state


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
    request.session['state'] = training_state

    # retrieve image pairs, shuffle them and put in session
    image_pair_ids = prepare_images(test_id)
    request.session['image_pair_ids'] = image_pair_ids
    request.session['image_pair_id_ptr'] = -1

    # retrieve related questions and put them in session
    training_image_pairs = TrainingImagePair.objects.all().order_by('id')
    context = {
        'test_title': test_instance.title,
        'training_image_pair_id': training_image_pairs[0].id if len(training_image_pairs) > 0 else 0

    }
    return render_to_response('test.html', context)


def prepare_images(test_id):
    image_pairs = ImagePair.objects.filter(test=test_id)
    image_pair_ids = []
    for pair in image_pairs:
        for i in range(pair.repeats):
            image_pair_ids.append(pair.id)
    shuffle(image_pair_ids)
    return image_pair_ids


def training(request, training_image_pair_id):
    training_image_pair_id = int(training_image_pair_id)
    test_id = request.session.get('test_id')
    training_image_pairs = TrainingImagePair.objects.all().order_by('id')

    for i in range(0, len(training_image_pairs)):
        if training_image_pairs[i].id == training_image_pair_id:
            if i != len(training_image_pairs) - 1:
                next_training_image_pair_id = training_image_pairs[i + 1].id
                prequestions = []
            else:
                next_training_image_pair_id = None
                prequestions = PreQuestion.objects.filter(test=test_id).order_by('order')
            context = {
                'text': training_image_pairs[i].text,
                'left': '/media/' + str(training_image_pairs[i].left),
                'right': '/media/' + str(training_image_pairs[i].right),
                'next_training_image_pair': next_training_image_pair_id,
                'question_id': next((q for q in prequestions if not q.isSeparator), None),
                'is_training': True
            }
            return render_to_response('image_pair.html', context)
    return HttpResponseNotFound('Страница недоступна')


def question(request, question_id):
    question_id = int(question_id)
    state = request.session.get('state')

    if state == training_state:
        request.session['state'] = prequestions_state

    test_id = request.session.get('test_id')
    if test_id is None:
        return HttpResponseNotFound('Вопрос недоступен')

    if request.session.get('state') == prequestions_state:
        model = PreQuestion
    elif request.session.get('state') == postquestions_state:
        model = PostQuestion
    else:
        return HttpResponseNotFound('Вопрос недоступен')

    questions = model.objects.filter(test=test_id).order_by('order')

    if len(questions) == 0:
        return HttpResponseNotFound('Вопросов к этому тесту не найдено')

    if question_id not in list(map(lambda q: q.id, questions)):
        return HttpResponseNotFound('Вопрос недоступен')

    separator_found = False
    first_found = False
    prev_id = None
    next_id = None

    actual_questions = []

    for i in range(0, len(questions)):
        if questions[i].isSeparator:
            if len(actual_questions) == 0:
                continue
            else:
                separator_found = True
        else:
            if separator_found:
                next_id = questions[i].id
                break
            else:
                if questions[i].id == question_id:
                    actual_questions.append(questions[i])
                    first_found = True
                else:
                    if first_found:
                        actual_questions.append(questions[i])
                    else:
                        prev_id = questions[i].id

    if len(actual_questions) == 0:
        return HttpResponseNotFound('Такого вопроса не существует')

    question_titles_and_answers = []

    for q in actual_questions:
        question_titles_and_answers.append((q.title, Answer.objects.filter(question=q.id)))

    question_instance = model.objects.get(id=question_id)
    context = {
        'titles': question_instance.title,
        'qta': question_titles_and_answers,
        'prev_id': prev_id,
        'next_id': next_id
    }
    return render_to_response('question.html', context)




def pairs(request):
    if request.session.get('state') != pairs_state:
        return HttpResponseNotFound('Страница недоступна')

    image_pair_ids = request.session.get('image_pair_ids')

    ptr = request.session.get('image_pair_id_ptr') + 1
    if ptr > len(image_pair_ids) - 1:
        return HttpResponseNotFound('Пикчи кончились')

    request.session['image_pair_id_ptr'] = ptr
    image_pair = ImagePair.objects.get(id=image_pair_ids[ptr])
    left = '/media/' + str(image_pair.left.img)
    right = '/media/' + str(image_pair.right.img)

    context = {
        'left': left,
        'right': right,
        'is_training': False
    }
    return render_to_response('image_pair.html', context)


def go_to_pairs(request):
    if request.session.get('state') == prequestions_state:
        request.session['state'] = pairs_state
        return redirect('/pairs')
    else:
        return HttpResponseNotFound('Страница недоступна')