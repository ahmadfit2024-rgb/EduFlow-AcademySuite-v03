from django.views.generic import TemplateView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from bson import ObjectId
from .models import Course, LearningPath, Lesson, Question
from .forms import LearningPathForm, LessonForm, QuestionForm
from apps.enrollment.models import Enrollment

# ... (Other views remain the same) ...

class TakeQuizView(LoginRequiredMixin, DetailView):
    """
    Displays the quiz interface for the student to take the test.
    """
    model = Course
    template_name = 'learning/take_quiz.html'
    pk_url_kwarg = 'course_pk'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson_id = self.kwargs['lesson_id']
        lesson = next((l for l in self.object.lessons if str(l._id) == lesson_id), None)

        if not lesson or lesson.content_type != 'quiz':
            return redirect('dashboard')

        context['lesson'] = lesson
        return context

class QuizResultView(LoginRequiredMixin, DetailView):
    """
    Displays the results of a specific quiz attempt.
    """
    model = Enrollment
    template_name = 'learning/quiz_result.html'
    pk_url_kwarg = 'enrollment_pk'
    context_object_name = 'enrollment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt_id = self.kwargs['attempt_id']
        
        # Find the specific attempt from the enrollment's history
        attempt = next((att for att in self.object.quiz_attempts if att['attempt_id'] == attempt_id), None)
        
        if not attempt:
            return redirect('dashboard')
            
        context['attempt'] = attempt
        return context