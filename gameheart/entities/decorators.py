#Decorators

from django.http import HttpResponseRedirect
from gameheart.entities.models import UserProfile

def check_terms(function):
    def wrap(request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        if profile.acceptedterms == False:
            action = request.path_info
            red = ''.join(['/terms/?next=',action])
            return HttpResponseRedirect(red)
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap
