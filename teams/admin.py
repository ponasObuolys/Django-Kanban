from django.contrib import admin
from .models import Team, TeamMembership, TeamInvitation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'owner__username')
    date_hierarchy = 'created_at'

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('team', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('team__name', 'user__username')
    date_hierarchy = 'joined_at'

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'invited_user', 'invited_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('team__name', 'invited_user__username', 'invited_by__username')
    date_hierarchy = 'created_at'
