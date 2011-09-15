from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.template.context import RequestContext
from models import Quiz, Question, UserProfile, Level
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ('name', 'username', 'password1', 'password2', 'email',)

def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
    
    template_data = {
        'title': 'ZYXT - Registration',
        'form': form,
    }
    return render_to_response('registration/registration.html', template_data, context_instance=RequestContext(request))

def halls_of_fame(request, id=None):
    if not id:
        quizzes = Quiz.objects.filter(display='Y')
        template_data = {
                        'title': 'ZYXT - Halls of Fame',
                        'quizzes': quizzes,
                        }
        return render_to_response('halls_of_fame.html', template_data, context_instance=RequestContext(request))
    else:
        PAGINATE_BY = 10
        
        quiz = get_object_or_404(Quiz, id=id)
        
        page = int(request.GET.get('page', 1))
        start = (page-1) * PAGINATE_BY
        end = start + PAGINATE_BY
        
        try:
            quiz.level_set.order_by('-level')[end]
            nextPage = page+1
        except IndexError:
            nextPage = 0
        
        template_data = {
            'title': 'ZYXT - Halls of Fame',
            'page': page,
            'nextPage': nextPage,
            'prevPage': page-1,
            'quiz': quiz,
            'levels': quiz.level_set.order_by('-level')[start:end],
        }
        return render_to_response('halls_of_fame.html', template_data, context_instance=RequestContext(request))

def quiz_index(request):
    quizzes = Quiz.objects.filter(display='Y')
    
    template_data = {
        'title': 'ZYXT - Quizzes',
        'quizzes': quizzes,
    }
    return render_to_response('quiz_index.html', template_data, context_instance=RequestContext(request))

def quiz_description(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    template_data = {
        'title': 'ZYXT - Quiz',
        'quiz': quiz,
    }
    return render_to_response('quiz_description.html', template_data, context_instance=RequestContext(request))

@login_required
def quiz(request, id, level, restart=0):
    quiz = get_object_or_404(Quiz, id=id)
    
    # Check whether the current user has started the quiz before
    user = get_object_or_404(UserProfile, username=request.user)
    try:
        user.level_set.get(quiz=id)
    except Level.DoesNotExist:
        user.level_set.create(quiz=quiz, level=1)
    
    # Check whether the current user is permitted to view this level
    current_level = int(user.level_set.get(quiz=id).level)
    if int(level) > current_level:
        return render_to_response('cheating.html', {}, context_instance=RequestContext(request))
    
    # Check if user is restarting the quiz
    if restart:
        return HttpResponseRedirect('/quiz/%s/%s/' % (id, current_level))
    
    # Check whether quiz is closed
    closed = quiz.is_closed()
    if closed:
        template_data = {
            'title': 'ZYXT - Quiz',
            'quiz': quiz,
            'content': closed,
        }
        return render_to_response('quiz.html', template_data, context_instance=RequestContext(request))
    
    # Check if questions have been added to the quiz
    if not quiz.has_questions():
        template_data = {
            'title': 'ZYXT - Quiz',
            'quiz': quiz,
            'content': 'Questions are yet to be added to this quiz. Kindly check later.',
        }
        return render_to_response('quiz.html', template_data, context_instance=RequestContext(request))
    
    # Check if user has completed the quiz
    highest_level = int(quiz.question_set.order_by('-level')[0].level)
    if int(level) > highest_level:
        template_data = {
            'title': 'ZYXT - Quiz',
            'quiz': quiz,
            'content': 'Congratulations. You have completed the quiz.',
        }
        return render_to_response('quiz.html', template_data, context_instance=RequestContext(request))
    
    try:
        question = quiz.question_set.get(level=level)
    except Question.DoesNotExist:
        raise Http404
    
    error = ''
    if request.POST:
        answer = request.POST.get('answer')
        if answer in question.answers.split():
            # Promote the user
            if int(level) == current_level:
                level_object = user.level_set.get(quiz=id)
                level_object.level += 1
                level_object.save()
            # Display next level
            next_level = '/quiz/%d/%d' % (int(id), int(level) + 1)
            return HttpResponseRedirect(next_level)
        else:
            error = 'Wrong Answer. Try Again.'
    
    template_data = {
        'title': 'ZYXT - Quiz',
        'quiz': quiz,
        'uri': 'http://zyxt.in%s' % (request.path,),
        'error': error,
        'question': question.question,
    }
    
    return render_to_response('quiz.html', template_data, context_instance=RequestContext(request))
