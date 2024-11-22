from django.urls import path
from .views import ProcessAudioView, SubmitAudioView, AccRatingView, GetGrievanceRecordsView, HelloView

urlpatterns = [
    path('process_audio/', ProcessAudioView.as_view(), name='process_audio'),
    path('submit_audio/', SubmitAudioView.as_view(), name='submit_audio'),
    path('acc_rating/', AccRatingView.as_view(), name='acc_rating'),
    path('get_grievance_records/', GetGrievanceRecordsView.as_view(), name='get_grievance_records'),
    path("hello/", HelloView.as_view(), name='hello')
]
