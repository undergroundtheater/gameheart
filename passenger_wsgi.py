#Import sys and os modules
import sys, os
#We want virt_binary to point to our virtualenv binary
virt_binary = "/home/undergro/djangoenv/bin/python"
#The system python binary is not our virtualenv binary so we are going to execute our virtualenv python instead
if sys.executable != virt_binary: os.execl(virt_binary, virt_binary, *sys.argv)
sys.path.append(os.getcwd())
#This points the environment to our settings file as a relative path to the passenger_wsgi.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "gameheart.settings"
#import our django stuff
import django.core.handlers.wsgi
#Tell passenger where the application is:
application = django.core.handlers.wsgi.WSGIHandler()
