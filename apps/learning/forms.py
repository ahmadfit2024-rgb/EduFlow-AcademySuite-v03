from django import forms
from django.forms import inlineformset_factory
from .models import Course, LearningPath, Lesson, Question, Answer

# ... (CourseForm and LearningPathForm remain the same) ...
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 
            'slug', 
            'description', 
            'instructor', 
            'category', 
            'status', 
            'cover_image_url'
        ]

class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ['title', 'description', 'supervisor']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LessonForm(forms.ModelForm):
    video_url = forms.URLField(required=False, label="Video URL (Vimeo or YouTube)")
    
    class Meta:
        model = Lesson
        fields = ['title', 'content_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

# --- New Forms for Quiz Builder ---

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']
        widgets = {
            'answer_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter answer text'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter the question text'}),
        }

# A FormSet for managing multiple answers for a single question
AnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    form=AnswerForm, 
    extra=4, # Start with 4 answer fields
    can_delete=True,
    fk_name='question' # Explicitly define the foreign key relationship for clarity
)