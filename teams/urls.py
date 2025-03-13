from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.team_create, name='team_create'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('<int:team_id>/delete/', views.team_delete, name='team_delete'),
    
    # Team Membership
    path('<int:team_id>/members/', views.team_members, name='team_members'),
    path('<int:team_id>/members/add/', views.add_member, name='add_member'),
    path('<int:team_id>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    path('<int:team_id>/members/<int:user_id>/role/', views.change_member_role, name='change_member_role'),
    
    # Team Invitations
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('<int:team_id>/invite/', views.send_invitation, name='send_invitation'),
    path('invitations/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitations/<int:invitation_id>/reject/', views.reject_invitation, name='reject_invitation'),
    path('invitations/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    
    # Test views
    path('test-form/', views.test_form, name='test_form'),
] 