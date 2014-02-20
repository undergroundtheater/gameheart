
from django.dispatch import dispatcher
from django.db.models import signals

import models

def post_syncdb(signal, sender, app, created_models, **kwargs):
    # only run when our model got created
    if (signal == signals.post_syncdb) and (app == models):
        models.install()

signals.post_syncdb.connect(post_syncdb)
