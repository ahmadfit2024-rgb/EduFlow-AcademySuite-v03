from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from .models import DiscussionThread
from .forms import DiscussionThreadForm
from apps.learning.models import Course

class AddDiscussionThreadView(LoginRequiredMixin, CreateView):
    """
    Handles the creation of a new discussion thread for a specific lesson,
    driven by an HTMX request from the course player.
    """
    model = DiscussionThread
    form_class = DiscussionThreadForm
    
    def form_valid(self, form):
        course_id = self.request.POST.get('course_id')
        lesson_id = self.kwargs.get('lesson_id')
        course = get_object_or_404(Course, pk=course_id)
        
        thread = form.save(commit=False)
        thread.student = self.request.user
        thread.course_id = course_id
        thread.lesson_id = lesson_id
        thread.save()

        threads = DiscussionThread.objects.filter(lesson_id=lesson_id).order_by('-created_at')
        context = {
            'threads': threads,
            'course': course,
            'current_lesson_id': lesson_id,
            'form': DiscussionThreadForm()
        }
        
        response = render(self.request, 'interactions/partials/_discussion_forum_content.html', context)
        response['HX-Trigger-Detail'] = '{"message": "Your question has been posted successfully!"}'
        response['HX-Trigger'] = 'showToast'
        return response

class AIChatFormView(LoginRequiredMixin, TemplateView):
    """
    Renders the partial template for the AI chat form, including
    the necessary context (course and lesson IDs).
    """
    template_name = 'interactions/partials/_ai_chat_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'course_pk': self.kwargs.get('course_pk'),
            'lesson_id': self.kwargs.get('lesson_id'),
        })
        return context