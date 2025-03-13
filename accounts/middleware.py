from django.middleware.csrf import get_token

class EnsureCsrfCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force CSRF cookie to be set
        csrf_token = get_token(request)
        print(f"DEBUG MIDDLEWARE: CSRF token set: {csrf_token[:10]}... (first 10 chars)")
        
        # Process the request
        response = self.get_response(request)
        
        # Add debugging for POST requests
        if request.method == 'POST':
            csrf_present = 'CSRF_COOKIE' in request.META
            csrf_header = request.META.get('HTTP_X_CSRFTOKEN', None)
            print(f"DEBUG MIDDLEWARE: POST request detected")
            print(f"DEBUG MIDDLEWARE: CSRF cookie present: {csrf_present}")
            print(f"DEBUG MIDDLEWARE: CSRF header: {csrf_header[:10] + '...' if csrf_header else 'None'}")
        
        return response 