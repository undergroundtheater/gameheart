#gameheart.entities.forms

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gameheart.entities.models import *

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email',]
        widgets = {
            'password':forms.PasswordInput
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['isadmin','description']

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password':forms.PasswordInput
        }

class ChapterTypeForm(forms.ModelForm):
    class Meta:
        model = ChapterType
        fields = ['name', 'description']
    sname = Vocabulary.objects.get(name='ChapterType').displayname
    surl = '/types/chapters/'
    sheading = ''.join(['Add New ',sname])

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['name', 'type', 'description']
    sname = Vocabulary.objects.get(name='Chapter').displayname
    surl = '/chapters/'
    sheading = ''.join(['Add New ',sname])

class StaffTypeForm(forms.ModelForm):
    class Meta:
        model = StaffType
        fields = ['name', 'description']
    sname = Vocabulary.objects.get(name='StaffType').displayname
    surl = '/types/staff/'
    sheading = ''.join(['Add New ',sname])

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'type']
    sname = Vocabulary.objects.get(name='Staff').displayname
    surl = '/staff/'
    sheading = ''.join(['Add New ',sname])

class CharacterTypeForm(forms.ModelForm):
    class Meta:
        model = CharacterType
        fields = ['name', 'description']
    sname = Vocabulary.objects.get(name='CharacterType').displayname
    surl = '/types/characters/'
    sheading = ''.join(['Add New ',sname])

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'type', 'chapter', 'description']
    sname = Vocabulary.objects.get(name='Character').displayname
    surl = '/characters/'
    sheading = ''.join(['Add New ',sname])

class CharacterOwnerForm(forms.ModelForm):
    class Meta:
        model = CharacterOwner
        fields = ['user']
    sname = 'Character Owner'
    surl = '/characters/owners/'
    sheading = 'Assign Character to User'

class TraitTypeForm(forms.ModelForm):
    class Meta:
        model = TraitType
        fields = ['name', 'aggregate', 'description']
    sname = Vocabulary.objects.get(name='TraitType').displayname
    surl = '/types/traits/'
    sheading = ''.join(['Add New ',sname])

class TraitForm(forms.ModelForm):
    class Meta:
        model = Trait
        fields = ['name', 'type', 'level', 'xpcost', 'bpcost', 'description']
    sname = Vocabulary.objects.get(name='Trait').displayname
    surl = '/traits/'
    sheading = ''.join(['Add New ',sname])

class CharacterTraitForm(forms.ModelForm):
    class Meta:
        model = CharacterTrait
        fields = ['character', 'trait']
        widgets = {
            'character': forms.HiddenInput,
        }
    sname = 'Character Trait'
    surl = '/characters/traits/'
    sheading = 'Add New Trait to Character'
    sredirect = 'user_index'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['chapter', 'chapteraddress', 'dateheld']
        widgets = {
            'chapter': forms.HiddenInput,
        }
    sname = Vocabulary.objects.get(name='Event').displayname
    surl = '/events/'
    sheading = ''.join(['Add New ',sname])

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['subject', 'body']
    sname = Vocabulary.objects.get(name='Note').displayname
    surl = '/notes/'
    sheading = ''.join(['Add New ',sname])

class NoteTagForm(forms.ModelForm):
    class Meta:
        model = NoteTag
        fields = ['tag']
    sname = 'Note'
    surl = '/notes/tags/'
    sheading = 'Add New Note Tag'

class VocabularyForm(forms.ModelForm):
    class Meta:
        model = Vocabulary
        fields = ['displayname']
    sname = 'Vocabulary'
    surl = '/vocabulary/'
    sheading = 'vocabulary'
