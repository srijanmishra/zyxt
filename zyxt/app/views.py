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
    
    templateData = {
                    'title': 'ZYXT - Registration',
                    'form': form,
                    }
    return render_to_response('registration/registration.html', templateData, context_instance=RequestContext(request))

def halls_of_fame(request, id=None):
    if not id:
        quizzes = Quiz.objects.filter(display='Y')
        templateData = {
                        'title': 'ZYXT - Halls of Fame',
                        'quizzes': quizzes,
                        }
        return render_to_response('halls_of_fame.html', templateData, context_instance=RequestContext(request))
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
        
        templateData = {
                        'title': 'ZYXT - Halls of Fame',
                        'page': page,
                        'nextPage': nextPage,
                        'prevPage': page-1,
                        'quiz': quiz,
                        'levels': quiz.level_set.order_by('-level')[start:end],
                        }
        return render_to_response('halls_of_fame.html', templateData, context_instance=RequestContext(request))

def quiz_index(request):
    quizzes = Quiz.objects.filter(display='Y')
    
    templateData = {
                    'title': 'ZYXT - Quizzes',
                    'quizzes': quizzes,
                    }
    return render_to_response('quiz_index.html', templateData, context_instance=RequestContext(request))

def quiz_description(request, id):
    quiz = get_object_or_404(Quiz, id=id)
    templateData = {
                    'title': 'ZYXT - Quiz',
                    'quiz': quiz,
                    }
    return render_to_response('quiz_description.html', templateData, context_instance=RequestContext(request))

@login_required
def quiz(request, id, level, restart=0):
    quiz = get_object_or_404(Quiz, id=id)
    
    # Check whether the current user is permitted to view this level
    user = get_object_or_404(UserProfile, username=request.user)
    try:
        user.level_set.get(quiz=id)
    except Level.DoesNotExist:
        user.level_set.create(quiz=quiz, level=1)
    
    current_level = int(user.level_set.get(quiz=id).level)
    if int(level) > current_level:
        return render_to_response('cheating.html', {}, context_instance=RequestContext(request))
    
    # Check whether the time is right
    now = datetime.now()
    if quiz.start_time and quiz.start_time > now:
        templateData = {
                        'title': 'ZYXT - Quiz',
                        'quiz': quiz,
                        'content': 'This quiz has not started yet. Kindly check later.',
                        }
        return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
    if quiz.end_time and quiz.end_time < now:
        templateData = {
                        'title': 'ZYXT - Quiz',
                        'quiz': quiz,
                        'content': 'This quiz has ended. Meanwhile, you can try other quizzes.',
                        }
        return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
    
    # Check whether quiz is open yet
    if quiz.display == 'N':
        templateData = {
                        'title': 'ZYXT - Quiz',
                        'quiz': quiz,
                        'content': 'Quiz has not opened yet. Kindly check later.',
                        }
        return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
    
    # Check if questions have been added to the quiz
    if not quiz.question_set.order_by('-level'):
        templateData = {
                        'title': 'ZYXT - Quiz',
                        'quiz': quiz,
                        'content': 'Questions are yet to be added to this quiz. Kindly check later.',
                        }
        return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
    
    # Check if user has completed the quiz
    if int(level) > int(quiz.question_set.order_by('-level')[0].level):
        templateData = {
                        'title': 'ZYXT - Quiz',
                        'quiz': quiz,
                        'content': 'Congratulations. You have completed the quiz.',
                        }
        return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
    
    try:
        question = quiz.question_set.get(level=level)
    except Question.DoesNotExist:
        raise Http404
    
    # Check if user is restarting the quiz
    if restart:
        return HttpResponseRedirect('/quiz/%s/%s/' % (id, current_level))
    
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
    
    templateData = {
                    'title': 'ZYXT - Quiz',
                    'quiz': quiz,
                    'uri': 'http://zyxt.in%s' % (request.path,),
                    'error': error,
                    'question': question.question,
                    }
    
    return render_to_response('quiz.html', templateData, context_instance=RequestContext(request))
