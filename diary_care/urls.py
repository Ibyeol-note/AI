from django.urls import path
from .views import DiaryCareAPIView

urlpatterns = [
    path('', DiaryCareAPIView.as_view(), name='diary_care'),
]