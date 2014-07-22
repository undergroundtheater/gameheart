#validations.py

from django.db.models import Q
from datetime import datetime
from gameheart.entities.models import *

#def isactive(nmodel, nuser):
#    model = nmodel.objects.filter(dateactive

def userview(nuser):
    user = nuser
    profile = UserProfile.objects.get(user=nuser)
    if profile.isadmin == 1:
        return True
    else:
        return False
    
def userfilter(nmodel, nuser):
    user = nuser
    profile = UserProfile.objects.get(user=nuser)
    model = nmodel
    if model == 'Character':
        char_list = CharacterOwner.objects.filter(user__in=user)
        model = nmodel.objects.filter(character__in=char_list)
    elif model == 'Note':
        charo_list = CharacterOwner.objects.filter(user__in=user)
        char_list = Character.objects.filter(pk__in=charo_list.character.id)
        chap_list = Chapter.objects.filter(pk__in=char_list.chapter.id)
        ctrait_list = CharacterTrait.objects.filter(character__in=char_list)
        trait_list = Trait.objects.filter(pk__in=ctrait_list.trait.id)
        staff_list = Staff.objects.filter(user__in=user)
        noteowner_list = NoteOwner.objects.filter(Q(user__in=user) | Q(character__in=char_list) | Q(chapter__in=chap_list) | Q(trait__in=trait_list) | Q(pk__in=noteowner_list.note.id))
        model = Note.objects.filter(Q(pk__in=noteowner_list.note.id) | Q(author=user))
    else:
        model = nmodel.objects.all()
    return model

def notefilter(ntag, nuser):
    user = nuser
    profile = UserProfile.objects.get(user=nuser)
    tags = NoteTag.objects.filter(tag=ntag)
    notes = Note.objects.filter(self__in=tags.note)

def characterfilter(nuser, charid, ndate=None):
    user = nuser
    character = Character.objects.get(pk=charid)
    owner_list = CharacterOwner.objects.filter(Q(character=character)).filter(Q(user=user))
    if not owner_list:
        return False
    if ndate == None:
        date = datetime.now().replace(tzinfo=pytz.UTC)
    else:
        date = ndate
    chartraits = CharacterTrait.objects.all()#filter(Q(character=character)).filter(Q(dateactive == None)|Q(dateactive<=date)).filter(Q(dateexpiry == None)|Q(dateexpiry>=date))
    model = chartraits.select_related('trait')

