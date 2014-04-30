#Start Database

from gameheart.entities.models import *
from gameheart.entities.forms import *

user = User.objects.get(id=1)

try: 
	profile = UserProfile.objects.get(user=user)

except UserProfile.DoesNotExist:
	form = UserProfileForm()
	model_instance = form.save(commit=False)
	model_instance.user = user
	model_instance.save()

