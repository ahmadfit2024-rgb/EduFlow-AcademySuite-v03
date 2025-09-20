from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse
from bson import ObjectId
import uuid
from datetime import datetime
from apps.enrollment.models import Enrollment
from apps.learning.models import Course
from .serializers import EnrollmentSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    
    # ... (mark_lesson_complete action remains the same) ...

    @action(detail=False, methods=['post'], url_path='submit-quiz')
    def submit_quiz(self, request):
        """
        Receives quiz answers, grades them, saves the attempt, and returns the result URL.
        """
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        answers = request.data.get('answers', {})

        enrollment = get_object_or_404(Enrollment, student=user, enrollable_id=course_id)
        course = get_object_or_404(Course, pk=course_id)
        lesson = next((l for l in course.lessons if str(l._id) == lesson_id), None)

        if not lesson or lesson.content_type != 'quiz':
            return Response({'error': 'Lesson is not a quiz.'}, status=status.HTTP_400_BAD_REQUEST)

        total_questions = len(lesson.content_data.get('questions', []))
        correct_answers = 0
        
        # Grade the submission
        for i, question_data in enumerate(lesson.content_data['questions']):
            question_id = str(question_data['_id'])
            submitted_answer_id = answers.get(f'question_{i+1}')
            
            correct_answer = next((ans for ans in question_data['answers'] if ans['is_correct']), None)
            
            if correct_answer and submitted_answer_id == str(correct_answer['_id']):
                correct_answers += 1
        
        score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 100

        # Save the attempt
        attempt_id = str(uuid.uuid4())
        attempt_data = {
            'attempt_id': attempt_id,
            'lesson_id': lesson_id,
            'score': score,
            'submitted_at': datetime.utcnow().isoformat(),
            'answers': answers,
        }
        enrollment.quiz_attempts.append(attempt_data)
        enrollment.save()
        
        result_url = reverse('learning:quiz_result', kwargs={'enrollment_pk': enrollment.pk, 'attempt_id': attempt_id})
        
        return Response({'status': 'success', 'result_url': result_url}, status=status.HTTP_200_OK)