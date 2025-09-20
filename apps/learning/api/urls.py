from django.urls import path
from .views import AddDiscussionThreadView, AIChatFormView

app_name = 'interactions'

urlpatterns = [
    path('lessons/<str:lesson_id>/add-thread/', AddDiscussionThreadView.as_view(), name='add_thread'),
    
    # New URL to render the AI chat form partial
    path('ai-chat-form/course/<str:course_pk>/lesson/<str:lesson_id>/', AIChatFormView.as_view(), name='ai_chat_form'),
]