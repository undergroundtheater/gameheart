#gameheart.entities.models

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='connect')
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    isadmin = models.BooleanField( default=False )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( 'self', null=True )
    def __unicode__(self):
        return self.name

class ChapterType(models.Model):
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( ChapterType, related_name='+', null=True )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class ChapterAddress(models.Model):
    name = models.CharField( max_length=200 )
    chapter = models.ForeignKey( Chapter, related_name='+') 
    address1 = models.CharField( max_length=200, null=True )
    address2 = models.CharField( max_length=200, null=True )
    city = models.CharField( max_length=200, null=True )
    state = models.CharField( max_length=200, null=True )
    zip = models.CharField( max_length=200, null=True )
    def __unicode__(self):
        return self.name

class StaffType(models.Model):
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class Staff(models.Model):
    chapter = models.ForeignKey( Chapter, related_name='+' )
    user = models.ForeignKey( User, related_name='+' )
    type = models.ForeignKey( StaffType, related_name='+' )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class Event(models.Model):
    chapter = models.ForeignKey( Chapter, related_name='+' )
    chapteraddress = models.ForeignKey( ChapterAddress, related_name='+' )
    dateheld = models.DateTimeField( null=True )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class CharacterType(models.Model):
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class Character(models.Model):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( CharacterType, related_name='+' )
    chapter = models.ForeignKey( Chapter, related_name='+' )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class CharacterOwner(models.Model):
    character = models.ForeignKey( Character )
    user = models.ForeignKey( User, related_name='+' )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.character

class Attendance(models.Model):
    event = models.ForeignKey( Event, related_name='+', null=True )
    user = models.ForeignKey( User, related_name='+' )
    character = models.ForeignKey( Character, related_name='+' )
    xpawarded = models.IntegerField( null=True )
    hidden = models.BooleanField()
    authorizedby = models.ForeignKey( User, related_name='+' )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class TraitType(models.Model):
    name = models.CharField( max_length=200 )
    aggregate = models.BooleanField()
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class Trait(models.Model):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( TraitType, related_name='+' )
    level = models.IntegerField( default=1 )
    xpcost = models.IntegerField( default=0 )
    bpcost = models.IntegerField( default=0 )
    description = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

class TraitLimit(models.Model):
    trait = models.ForeignKey( Trait, related_name='+' )
    chaptertype = models.ForeignKey( ChapterType, related_name='+' )
    charactertype = models.ForeignKey( CharacterType, related_name='+' )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return str(self.charactertype) + '_' + str(self.trait)

class CharacterTrait(models.Model):
    character = models.ForeignKey( Character, related_name='+' )
    trait = models.ForeignKey( Trait, related_name='+' )
    authorizedby = models.ForeignKey( User, null=True, default=None )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return str(self.trait)

class Discount(models.Model):
    authorizedby = models.ForeignKey( User, related_name='+' )
    charactertrait = models.ForeignKey( CharacterTrait, related_name='+' )
    reason = models.TextField( blank=True )
    xpdiscount = models.IntegerField( default=0 )
    bpdiscount = models.IntegerField( default=0 )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return str(self.authorizedby) + '_' + str(self.charactertrait)

class Authorization(models.Model):
    issuer = models.ForeignKey( User, related_name='+' )
    charactertrait = models.ForeignKey( CharacterTrait, related_name='+' )
    reason = models.TextField( blank=True )
    authorizinguser = models.ForeignKey( User, related_name='+' )
    authorized = models.BooleanField( default=0 )
    dateauthorized = models.DateTimeField()
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class Note(models.Model):
    author = models.ForeignKey( User, related_name='+' )
    subject = models.CharField( max_length=200 )
    body = models.TextField( blank=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return str(self.subject)

class NoteTag(models.Model):
    note = models.ForeignKey( Note )
    tag = models.CharField( max_length=100 )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class NoteOwner(models.Model):
    note = models.ForeignKey( Note, related_name='+')
    user = models.ForeignKey( User, related_name='+', null=True )
    character = models.ForeignKey( Character, related_name='+', null=True )
    chapter = models.ForeignKey( Chapter, related_name='+', null=True )
    trait = models.ForeignKey( Trait, related_name='+', null=True )
    traitlevel = models.IntegerField( null=True )
    stafftype = models.ForeignKey( StaffType, related_name='+', null=True )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )

class Vocabulary(models.Model):
    name = models.CharField( max_length=200, unique=True )
    displayname = models.CharField( max_length=200 )
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, related_name='+', null=True )
    def __unicode__(self):
        return self.name

def install():
    # Create objects here using Django ORM
    user = User.objects.get(id=1)
    # Users
    UserProfile(user_id=1, isadmin=1).save()
    model = User.objects.create_user('miles', 'justmike2000@gmail.com', 'miles')
    UserProfile(user=model, isadmin=1).save()
    model = User.objects.create_user('mere', 'miagardener@gmail.com', 'mere')
    UserProfile(user=model, isadmin=1).save()
    # Vocabulary
    Vocabulary(name='User', displayname='Patron').save()
    Vocabulary(name='ChapterType', displayname='Setting').save()
    Vocabulary(name='Chapter', displayname='Chronicle').save()
    Vocabulary(name='StaffType', displayname='StaffType').save()
    Vocabulary(name='Staff', displayname='Staff').save()
    Vocabulary(name='Event', displayname='Game').save()
    Vocabulary(name='CharacterType', displayname='CharacterType').save()
    Vocabulary(name='Character', displayname='Character').save()
    Vocabulary(name='TraitType', displayname='TraitType').save()
    Vocabulary(name='Trait', displayname='Trait').save()
    Vocabulary(name='Note', displayname='Note').save()
    # Chapters(Settings)
    model = ChapterType(name='Camarilla')
    model.save()
    Chapter(type=model, name='Test Cam Site').save()
    model = ChapterType(name='Anarch')
    model.save()
    Chapter(type=model, name='Test Anarch Site').save()
    model = ChapterType(name='Sabbat')
    model.save()
    Chapter(type=model, name='Test Sabbat Site').save()
    # Character Types
    CharacterType(name='Vampire').save()
    # Traits
    model = TraitType(name='Archetype')
    model.save()
    Trait(type=model, name='Bravo', level=0).save()
    Trait(type=model, name='Architect', level=0).save()
    model = TraitType(name='Clan')
    model.save()
    Trait(type=model, name='Ventrue', level=0).save()
    Trait(type=model, name='Giovanni', level=0).save()
    model = TraitType(name='Temper', aggregate=1)
    model.save()
    Trait(type=model, name='Blood', level=1).save()
    Trait(type=model, name='Willpower', level=1).save()
    Trait(type=model, name='Morality', level=1).save()
    model = TraitType(name='Attribute', aggregate=1)
    model.save()
    Trait(type=model, name='Physical', level=0).save()
    Trait(type=model, name='Mental', level=0).save()
    Trait(type=model, name='Social', level=0).save()
    model = TraitType(name='Emphasis')
    model.save()
    Trait(type=model, name='Strength', level=0).save()
    Trait(type=model, name='Dexterity', level=0).save()
    Trait(type=model, name='Stamina', level=0).save()
    Trait(type=model, name='Charisma', level=0).save()
    Trait(type=model, name='Manipulation', level=0).save()
    Trait(type=model, name='Appearance', level=0).save()
    Trait(type=model, name='Perception', level=0).save()
    Trait(type=model, name='Intelligence', level=0).save()
    Trait(type=model, name='Wits', level=0).save()
    model = TraitType(name='Skill', aggregate=1)
    model.save()
    Trait(type=model, name='Academics', level=0).save()
    Trait(type=model, name='Animal Ken', level=0).save()
    Trait(type=model, name='Athletics', level=0).save()
    model = TraitType(name='Background', aggregate=1)
    model.save()
    Trait(type=model, name='Generation', level=1).save()
    Trait(type=model, name='Contacts', level=1).save()
    Trait(type=model, name='Allies', level=1).save()
    model = TraitType(name='Discipline', aggregate=1)
    model.save()
    Trait(type=model, name='Potence', level=0).save()
    Trait(type=model, name='Dominate', level=0).save()
    Trait(type=model, name='Necromancy', level=0).save()
    model = TraitType(name='Merit')
    model.save()
    Trait(type=model, name='Common Sense', level=4).save()
    Trait(type=model, name='Danger Sense', level=2).save()
    model = TraitType(name='Flaw')
    model.save()
    Trait(type=model, name='Derrangement', level=3).save()
    Trait(type=model, name='Conspicuous Consumption', level=4).save()
    model = TraitType(name='Status')
    model.save()
    Trait(type=model, name='Acknowledged', level=4).save()
    Trait(type=model, name='Respected', level=4).save()
    Trait(type=model, name='Knowledgeable', level=4).save()
