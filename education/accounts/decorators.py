from functools import wraps

from django.conf import settings
from django.contrib import messages

import requests

def check_recaptcha(view_func):
    def _wrapped_view(self, request, *args, **kwargs):
        request.recaptcha_is_valid = None

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        if result['success']:
            request.recaptcha_is_valid = True
        else:
            request.recaptcha_is_valid = False
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return view_func(self, request=request, *args, **kwargs)
    return _wrapped_view