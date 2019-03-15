from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.assignments, name='assignments'),
    path('new/', views.assignment_create, name='create_assignment'),
    path('<int:assignment_id>/', views.assignment_view, name='assignment_view'),
    path('<int:assignment_id>/edit', views.assignment_create, name='assignment_edit'),
    path('<int:assignment_id>/delete', views.assignment_delete, name='assignment_delete'),
    path('<int:assignment_id>/force/<int:user_id>', views.assignment_force, name='assignment_force'),
    path('api/', views.APIView.as_view(), name="api"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
