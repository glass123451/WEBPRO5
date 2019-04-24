import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from .forms import PollForm, CommentForm, PollModelForm, QuestionForm, ChoiceModelForm
from .models import Poll, Question, Answer, Comment


def my_login(request):
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user:
			login(request, user)

			next_url = request.POST.get('next_url')
			if next_url:
				return redirect(next_url)
			else:
				return redirect('index')
		else:
			context['username'] = username
			context['password'] = password
			context['error'] = 'Wrong username or password'

	next_url = request.GET.get('next')
	if next_url:
		context['next_url'] = next_url



	return render(request, template_name='polls/login.html', context= context)


def my_logout(request):
	logout(request)
	return redirect('login')

def index(request):

	poll_list = Poll.objects.annotate(question_count=Count('question'))
	# poll_list = Poll.objects.all()

	# for poll in poll_list:
	# 	question_count = Question.objects.filter(poll_id = poll.id).count()
	# 	poll.question_count = question_count

	context = {
		'page_title': 'My Polls',
		'poll_list': poll_list
	}
	return render(request, template_name ='polls/index.html', context= context)

@login_required
@permission_required('polls.view_poll')
def detail(request, poll_id):

	poll = Poll.objects.get(pk=poll_id)
	if request.method == 'POST':
		for question in poll.question_set.all():
			name = 'choice' + str(question.id)
			choice_id = request.POST.get(name)
			# print(choice_id)

			if choice_id:
				try:
					ans = Answer.objects.get(question_id = question.id)
					ans.choice_id = choice_id
					ans.save()

				except Answer.DoesNotExist:

					Answer.objects.create(
						choice_id = choice_id,
						question_id = question.id
					)
	# print(request.GET)

	return render(request, 'polls/detail.html', {'poll': poll})


@login_required
@permission_required('polls.add_poll')
def create(request):
	context = {}
	QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)
	if request.method == 'POST':
		form = PollModelForm(request.POST)
		formset = QuestionFormSet(request.POST)

		if form.is_valid():
			poll = form.save()

			if formset.is_valid():
				for question_form in formset:
					Question.objects.create(
						text=question_form.cleaned_data.get('text'),
						type=question_form.cleaned_data.get('type'),
						poll=poll
					)
				context['success'] = 'Poll %s is created successfully!' %poll.title

	else:
		form = PollModelForm()
		formset = QuestionFormSet()

	context['form'] = form
	context['formset'] = formset
	return render(request, 'polls/create.html', context=context)

def create_comment(request, poll_id):
	if request.method == 'POST':
		form = CommentForm(request.POST)

		if form.is_valid():
			Comment.objects.create(
				title=form.cleaned_data.get('title'),
				body=form.cleaned_data.get('body'),
				email=form.cleaned_data.get('email'),
				tel=form.cleaned_data.get('tel')
			)

	else:
		form = CommentForm()

	context = {'form': form, 'poll_id':poll_id}

	return render(request, 'polls/create-comment.html', context=context)

@login_required
@permission_required('polls.change_poll')
def update(request, poll_id):
	poll = Poll.objects.get(id=poll_id)
	QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)
	if request.method == 'POST':
		form = PollModelForm(request.POST, instance=poll)
		formset = QuestionFormSet(request.POST)

		if form.is_valid():
			form.save()
			if formset.is_valid():
				for question_form in formset:
					#Has question_id -> update
					if question_form.cleaned_data.get('question_id'):
						question = Question.objects.get(id = question_form.cleaned_data.get('question_id'))
						if question:
							question.text = question_form.cleaned_data.get('text')
							question.type = question_form.cleaned_data.get('type')
							question.save()
						#No question_id -> create a new question
					else:
						if question_form.cleaned_data.get('text'):
							Question.objects.create(
								text=question_form.cleaned_data.get('text'),
								type=question_form.cleaned_data.get('type'),
								poll=poll
							)
				return redirect('update_poll', poll_id=poll.id)

	else:
		form = PollModelForm(instance=poll)
		data=[]
		for question in poll.question_set.all():
			data.append(
				{
					'text': question.text,
					'type': question.type,
					'question_id': question.id
				}
			)
		formset = QuestionFormSet(initial=data)

	context = {'form': form, 'poll': poll, 'formset': formset}
	return render(request, 'polls/update.html', context=context)

@login_required
@permission_required('polls.change_poll')
def delete_question(request, question_id):
	question = Question.objects.get(id=question_id)
	question.delete()
	return redirect('update_poll', poll_id=question.poll.id)

@login_required
@permission_required('polls.change_poll')
def add_choice(request, question_id):
	question = Question.objects.get(id=question_id)

	context = {'question': question}

	return render(request, 'choices/add.html', context=context)

def add_choice_api(request, question_id):
	if request.method == 'POST':
		choice_list = json.loads(request.body)
		error_list = []

		for choice in choice_list:
			data = {
				'text': choice['text'],
				'value': choice['value'],
				'question': question_id
			}
			form = ChoiceModelForm(data)
			if form.is_valid():
				form.save()
			else:
				error_list.append(form.errors.as_text())
		if len(error_list) == 0:
			return JsonResponse({'message': 'success'}, status=200)
		else:
			return JsonResponse({'message': error_list}, status=400)
	return JsonResponse({'message': 'This API does not accept GET request'}, status=405)