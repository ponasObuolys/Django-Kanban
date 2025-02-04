from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from allauth.account.views import SignupView
from .forms import CustomUserChangeForm, NotificationPreferencesForm, CustomUserCreationForm

# Create your views here.

@method_decorator([ensure_csrf_cookie, csrf_protect], name='dispatch')
class CustomSignupView(SignupView):
    template_name = 'account/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csrf_token_value'] = self.request.META.get('CSRF_COOKIE', '')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your account has been created successfully!')
        return response

@login_required
def profile_view(request):
    return render(request, 'accounts/profile/profile.html', {
        'user': request.user
    })

@login_required
def settings_view(request):
    return render(request, 'accounts/settings/settings.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.bio = request.POST.get('bio', '')
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('accounts:settings_view')
    
    return redirect('accounts:settings_view')

@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('accounts:settings_view')

@login_required
def update_notifications(request):
    if request.method == 'POST':
        form = NotificationPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your notification preferences have been updated successfully.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('accounts:settings_view')

@login_required
def update_theme(request):
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            request.user.theme_preference = theme
            request.user.save()
            messages.success(request, 'Your theme preference has been updated successfully.')
        else:
            messages.error(request, 'Invalid theme selection.')
    
    return redirect('accounts:settings_view')
