from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

@login_required
@ensure_csrf_cookie
def test_form(request):
    """
    Paprastas testas patikrinti, ar formos veikia serveryje.
    Šis puslapis leidžia atlikti POST užklausą ir parodo gautus duomenis.
    """
    debug_info = {
        'request_method': request.method,
        'cookies': request.COOKIES,
        'csrf_token': request.META.get('CSRF_COOKIE', 'Nerasta'),
        'post_data': dict(request.POST.items()) if request.method == 'POST' else None,
        'headers': {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    }
    
    print("DEBUG TEST FORM: Užklausos informacija:")
    for key, value in debug_info.items():
        print(f"DEBUG TEST FORM: {key}: {value}")
    
    if request.method == 'POST':
        return render(request, 'teams/test_form.html', {
            'debug_info': debug_info,
            'success': True,
            'post_data': request.POST
        })
    
    return render(request, 'teams/test_form.html', {
        'debug_info': debug_info
    }) 