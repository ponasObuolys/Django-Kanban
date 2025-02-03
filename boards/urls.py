from django.urls import path
from . import views

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('create/', views.board_create, name='board_create'),
    path('<int:board_id>/', views.board_detail, name='board_detail'),
    path('<int:board_id>/edit/', views.board_edit, name='board_edit'),
    path('<int:board_id>/delete/', views.board_delete, name='board_delete'),
    
    # Column URLs
    path('<int:board_id>/columns/create/', views.column_create, name='column_create'),
    path('columns/<int:column_id>/edit/', views.column_edit, name='column_edit'),
    path('columns/<int:column_id>/delete/', views.column_delete, name='column_delete'),
    
    # Task URLs
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/assign/', views.task_assign, name='task_assign'),
    
    # Task Comments
    path('tasks/<int:task_id>/comments/add/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Task Attachments
    path('tasks/<int:task_id>/attachments/add/', views.add_attachment, name='add_attachment'),
    path('attachments/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Labels
    path('<int:board_id>/labels/create/', views.label_create, name='label_create'),
    path('labels/<int:label_id>/edit/', views.label_edit, name='label_edit'),
    path('labels/<int:label_id>/delete/', views.label_delete, name='label_delete'),
    
    # API endpoints for drag and drop
    path('api/tasks/update-position/', views.update_task_position, name='update_task_position'),
    path('api/columns/update-position/', views.update_column_position, name='update_column_position'),
] 