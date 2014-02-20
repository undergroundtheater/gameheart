#Start Database

from gameheart.entities import models
from gameheart.entities import forms

user = User.objects.get(id=1)
has_profile = UserProfile.objects.get(user=user).count()
if user:
    if has_profile:
        form = UserProfileForm()
        model_instance = form.save(commit=False)
        model_instance.user = user
        model_instance.save()
