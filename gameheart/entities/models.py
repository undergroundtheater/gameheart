#gameheart.entities.models

from datetime import datetime
from django.db import models
from django.db.models import Q
from django.db import DEFAULT_DB_ALIAS
from django.contrib.auth.models import User
import pytz

class GHModel(models.Model):
    class Meta:
        abstract = True
    dateactive = models.DateTimeField( blank=True, null=True, default=None )
    dateexpiry = models.DateTimeField( blank=True, null=True, default=None )
    datecreated = models.DateTimeField( auto_now_add=True )
    datemodified = models.DateTimeField( auto_now=True )
    modifiedby = models.ForeignKey( User, null=True, related_name='+' )
    modifiedbyip = models.CharField( max_length=200, null=True )

class GHManager(models.Manager):
    def activeonly(self,date=None):
        model = self.model
        if date == None:
            date = datetime.now().replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=pytz.UTC)
        return self.filter(Q(dateactive=None)|Q(dateactive__lte=date)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=date))
    def seek(self, seekval):
        model = self.filter(name__icontains=seekval)
        return model
    def exists(self):
        if self:
            return True
        else:
            return False

class UserProfile(GHModel):
    user = models.ForeignKey(User, unique=True, related_name='connect')
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    isadmin = models.BooleanField( default=False )
    subscriptionlevel = models.IntegerField( default=0 )
    accountid = models.CharField( max_length=9, blank=True )
    acceptedterms = models.BooleanField()
    objects = GHManager()
    def __unicode__(self):
        return self.name

class ChapterType(GHModel):
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class Chapter(GHModel):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( ChapterType, related_name='chapter_type', null=True )
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

    def purge_killed(self):
        killed = Trait.objects.get(name='Dead', type=TraitType.objects.get(name='State'))
        chars = Character.objects.filter(chapter=self).all()

        for char in chars:
            if killed in char.character_trait_character.all().values('trait'):
                char.delete()

        

class ChapterAddress(GHModel):
    name = models.CharField( max_length=200 )
    chapter = models.ForeignKey( Chapter, related_name='address_chapter') 
    address1 = models.CharField( max_length=200, null=True )
    address2 = models.CharField( max_length=200, blank=True, null=True )
    city = models.CharField( max_length=200, null=True )
    state = models.CharField( max_length=200, null=True )
    zip = models.CharField( max_length=200, null=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class StaffType(GHModel):
    name = models.CharField( max_length=200 )
    isapprover = models.BooleanField()
    isdirector = models.BooleanField()
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class StaffManager(GHManager):
    def linkedonly(self,chapter):
        model = self.activeonly().filter(chapter=chapter)
        return model
    def approver(self):
        approvers = StaffType.objects.activeonly().filter(isapprover=True)
        model = self.activeonly().filter(type__in=approvers)
        return model
    def director(self):
        directors = StaffType.objects.activeonly().filter(isdirector=True)
        model = self.activeonly().filter(type__in=directors)
        return model

class Staff(GHModel):
    chapter = models.ForeignKey( Chapter, related_name='+' )
    user = models.ForeignKey( User, related_name='+' )
    type = models.ForeignKey( StaffType, related_name='+' )
    objects = StaffManager()

class Event(GHModel):
    name = models.CharField( max_length=200, blank=True)
    chapter = models.ForeignKey( Chapter, related_name='event_chapter' )
    chapteraddress = models.ForeignKey( ChapterAddress, related_name='+' )
    dateheld = models.DateTimeField( null=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class CharacterType(GHModel):
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class CharacterManager0(GHManager):
    def playableonly(self, user):
        owned = CharacterOwner.objects.activeonly().filter(user=user)
        inactivetraits = Trait.objects.activeonly().filter(Q(name='Dead')|Q(name='Shelved'))
        inactive = CharacterTrait.objects.activeonly().filter(trait__in=inactivetraits)
        model = self.activeonly().filter(pk__in=owned).exclude(pk__in=inactive)
        return model

    def deadonly(self):
        killed = Trait.objects.filter(name='Dead', type=TraitType.objects.filter(name='State')).get()
        model = self.filter(
                pk__in=CharacterTrait.objects.activeonly().filter(trait=killed).all().values('character'))
        return model

    def aliveonly(self):
        ticking = Trait.objects.filter(name='Active', type=TraitType.objects.filter(name='State')).get()
        model = self.filter(
                pk__in=CharacterTrait.objects.activeonly().filter(trait=ticking).all().values('character'))
        return model

class CharacterManager(CharacterManager0):
    def primaryexists(self,user,model):
        chapter = model.chapter
        chaptertype = ChapterType.objects.get(pk=chapter.type.id)
        chapters = Chapter.objects.filter(type=chaptertype.id)
        pcharacters = self.playableonly(user).filter(isprimary=1).filter(chapter__in=chapters)
        if pcharacters:
            return True
        else:
            return False

class Character(GHModel):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( CharacterType, related_name='character_type' )
    chapter = models.ForeignKey( Chapter, related_name='Character_chapter' )
    isnew = models.BooleanField()
    isprimary = models.BooleanField()
    public_description = models.TextField( blank=True )
    private_description = models.TextField( blank=True )
    objects = CharacterManager()
    def __unicode__(self):
        return self.name

    def is_dead(self):
        killed = Trait.objects.get(name='Dead', type=TraitType.objects.get(name='State'))
        try:
            dead = self.character_trait_character.filter(trait=killed)
            if dead:
                return True

        except:
            pass

        return False

class CharacterOwnerManager(GHManager):
    def linkedonly(self,character):
        model = self.activeonly().filter(character=character)
        return model

class CharacterOwner(GHModel):
    character = models.ForeignKey( Character )
    user = models.ForeignKey( User, related_name='character_owner' )
    iscontroller = models.BooleanField( default=False )
    objects = CharacterOwnerManager()
    def __unicode__(self):
        return self.character

class AttendanceManager(GHManager):
    def linkedonly(self,event):
        model = self.activeonly().filter(event=event)
        return model

class Attendance(GHModel):
    event = models.ForeignKey( Event, related_name='+', null=True )
    user = models.ForeignKey( User, related_name='attendee' )
    character = models.ForeignKey( Character, related_name='attended_character' )
    xpawarded = models.IntegerField( null=True )
    ishidden = models.BooleanField()
    authorizedby = models.ForeignKey( User, related_name='attendance_authuser', blank=True ,null=True, default=None)
    rejectedby = models.ForeignKey( User, related_name='attendance_rejuser', blank=True ,null=True, default=None)
    objects = AttendanceManager()

class TraitManager(GHManager):
    def clans(self):
        traittype = TraitType.objects.activeonly().get(name='Clan')
        return self.activeonly().filter(type=traittype)
    def cotraits(self):
        traittypes = TraitType.objects.activeonly().filter(cotrait = True)
        return self.activeonly().filter(type__in=traittypes)

class TraitType(GHModel):
    name = models.CharField( max_length=200 )
    aggregate = models.BooleanField()
    onepercharacter = models.BooleanField()
    multiplyxp = models.BooleanField()
    cotrait = models.BooleanField()
    availtocontroller = models.BooleanField()
    availtoapprover = models.BooleanField()
    availtodirector = models.BooleanField()
    labelable = models.BooleanField()
    xpcost1 = models.IntegerField( default=0 )
    xpcost2 = models.IntegerField( default=0 )
    xpcost3 = models.IntegerField( default=0 )
    xpcost4 = models.IntegerField( default=0 )
    xpcost5 = models.IntegerField( default=0 )
    description = models.TextField( blank=True )
    charactertypes = models.ManyToManyField( CharacterType, blank=True )
    chaptertypes = models.ManyToManyField( ChapterType, blank=True )
    objects = TraitManager()
    def __unicode__(self):
        return self.name

class Trait(GHModel):
    name = models.CharField( max_length=200 )
    type = models.ForeignKey( TraitType, related_name='trait_type' )
    isadmin = models.BooleanField( default=False )
    renamable = models.BooleanField( default=False )
    level = models.IntegerField( default=1 )
    description = models.TextField( blank=True )
    charactertypes = models.ManyToManyField( CharacterType, blank=True )
    chaptertypes = models.ManyToManyField( ChapterType, blank=True )
    cotraits = models.ManyToManyField( 'Trait', blank=True, related_name='cotrait')
    bantraits = models.ManyToManyField( 'Trait', blank=True, related_name='bantrait')
    addtraits = models.ManyToManyField( 'Trait', blank=True, related_name='addtrait')
    objects = TraitManager()
    def __unicode__(self):
        return self.name
    def cotrait_label(self):
        return ' - '.join([self.type.name,self.name])

class CharacterTraitManager0(GHManager):
    def showonly(self,date=None):
        if date == None:
            date = datetime.now().replace(tzinfo=pytz.UTC)
        return self.filter(Q(dateactive=None)|Q(dateactive__lte=date)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=date)).filter(Q(dateremoved=None)|Q(dateremoved__gte=date))
    def sheetonly(self,date=None):
        if date == None:
            date = datetime.now().replace(tzinfo=pytz.UTC)
        return self.filter(Q(dateactive=None)|Q(dateactive__lte=date)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=date)).filter(Q(dateremoved=None)|Q(dateremoved__gte=date)).exclude(authorizedby=None)

class CharacterTraitManager(CharacterTraitManager0):
    def sfilter(self, character, trait=None, traittype=None, showonly=False, date=None):
        if traittype != None:
            ttype = TraitType.objects.activeonly(date).filter(name=traittype)
        else:
            ttype = TraitType.objects.activeonly(date)
        if trait != None:
            traits = Trait.objects.activeonly(date).filter(type__in=ttype).filter(name=trait)
        else:
            traits = Trait.objects.activeonly(date).filter(type__in=ttype)
        if showonly == True:
            return self.showonly(date).filter(character=character).filter(trait__in=traits)
        else:
            return self.activeonly(date).filter(character=character).filter(trait__in=traits)

class CharacterTrait(GHModel):
    character = models.ForeignKey( Character, related_name='character_trait_character' )
    trait = models.ForeignKey( Trait, related_name='character_trait_trait' )
    label = models.CharField( max_length=200, blank=True, null=True )
    iscreation = models.BooleanField( default=False)
    isfree = models.BooleanField( default=False)
    authorizedby = models.ForeignKey( User, blank=True, null=True, default=None, related_name='character_trait_auth_user' )
    dateauthorized = models.DateTimeField( blank=True, null=True, default=None )
    dateremoved = models.DateTimeField( blank=True, null=True, default=None )
    objects = CharacterTraitManager()
    def __unicode__(self):
        name = self.trait.name
        if self.label !=None:
            name = self.label
        return str(name)

class TraitLimit(GHModel):
    trait = models.ForeignKey( Trait, related_name='trait_limit_trait' )
    requiredtrait = models.ForeignKey( Trait, related_name='trait_limit_required_trait' )
    level = models.IntegerField( blank=True )
    objects = GHManager()

class TraitLabel(GHModel):
    character = models.ForeignKey( Character, related_name='trait_label_character' )
    trait = models.ForeignKey( Trait, related_name='trait_label_trait' )
    label = models.CharField( max_length=200, blank=True, null=True )
    authorizedby = models.ForeignKey( User, related_name='trait_label_authuser', null=True, blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.label

class Discount(GHModel):
    authorizedby = models.ForeignKey( User, related_name='discount_authuser' )
    charactertrait = models.ForeignKey( CharacterTrait, related_name='discount_character_trait' )
    reason = models.TextField( blank=True )
    xpdiscount = models.IntegerField( default=0 )
    bpdiscount = models.IntegerField( default=0 )
    objects = GHManager()
    def __unicode__(self):
        return str(self.authorizedby) + '_' + str(self.charactertrait)

class Authorization(GHModel):
    issuer = models.ForeignKey( User, related_name='auth_issuer' )
    charactertrait = models.ForeignKey( CharacterTrait, related_name='auth_character_trait' )
    reason = models.TextField( blank=True )
    authorizinguser = models.ForeignKey( User, related_name='auth_user' )
    authorized = models.BooleanField( default=0 )
    dateauthorized = models.DateTimeField()
    objects = GHManager()

class Note(GHModel):
    author = models.ForeignKey( User, related_name='note_author' )
    subject = models.CharField( max_length=200 )
    body = models.TextField( blank=True )
    character = models.ManyToManyField( Character, blank=True )
    chapter = models.ManyToManyField( Chapter, blank=True )
    trait = models.ManyToManyField( Trait, blank=True )
    traitlevel = models.IntegerField( null=True )
    stafftype = models.ManyToManyField( StaffType, blank=True )
    objects = GHManager()
    def __unicode__(self):
        return str(self.subject)

class NoteTag(GHModel):
    note = models.ForeignKey( Note )
    tag = models.CharField( max_length=100 )
    objects = GHManager()

class NoteOwner(GHModel):
    note = models.ForeignKey( Note, related_name='note_owner_note')
    user = models.ForeignKey( User, related_name='note_owner', null=True )
    character = models.ForeignKey( Character, related_name='note_owner_character', null=True )
    chapter = models.ForeignKey( Chapter, related_name='note_owner_chapter', null=True )
    trait = models.ForeignKey( Trait, related_name='note_owner_trait', null=True )
    traitlevel = models.IntegerField( null=True )
    stafftype = models.ForeignKey( StaffType, related_name='note_owner_staff_type', null=True )
    objects = GHManager()

class Vocabulary(GHModel):
    name = models.CharField( max_length=200, unique=True )
    displayname = models.CharField( max_length=200 )
    displayplural = models.CharField( max_length=200, blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class Property(GHModel):
    name = models.CharField( max_length=200, unique=True )
    displayname = models.CharField( max_length=200 )
    floatvalue = models.FloatField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class FavoriteUser(GHModel):
    user = models.ForeignKey( User, related_name='favoring_user+' )
    favoriteuser = models.ForeignKey( User, related_name='favorite_user+')
    objects = GHManager()

class FavoriteChapter(GHModel):
    user = models.ForeignKey( User, related_name='favoring_user+' )
    favoritechapter = models.ForeignKey( Chapter, related_name='favorite_chapter+' )
    objects = GHManager()

class FavoriteCharacter(GHModel):
    user = models.ForeignKey( User, related_name='favoring_user+' )
    favoritecharacter = models.ForeignKey( Character, related_name='favorite_character+' )
    objects = GHManager()

class ImageLinks(GHModel):
    link = models.CharField( max_length=1000, blank=True )
    modelname = models.CharField( max_length=200, blank=True )
    modelid = models.IntegerField( blank=True )
    otherinfo = models.CharField( max_length=1000, blank=True )
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    objects = GHManager()

class Poll(GHModel):
    TYPE_CHOICES = ((0,'Single'),(1,'Multiple'),)
    name = models.CharField( max_length=200 )
    type = models.IntegerField( choices=TYPE_CHOICES, default=0 )
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class PollChoice(GHModel):
    poll = models.ForeignKey( Poll, related_name='+' )
    name = models.CharField( max_length=200 )
    description = models.TextField( blank=True )
    objects = GHManager()
    def __unicode__(self):
        return self.name

class PollUserChoice(GHModel):
    user = models.ForeignKey( User, related_name='polluser+' )
    poll = models.ForeignKey( Poll, related_name='+' )
    choice = models.ForeignKey( PollChoice, blank=True, related_name='choice' )
    choices = models.ManyToManyField( PollChoice, blank=True, related_name='choices' )
    description = models.TextField( blank=True )
    objects = GHManager()

class Transaction(GHModel):
    user = models.ForeignKey( User, related_name='txnuser+' )
    txnid = models.CharField( max_length=200, blank=True )
    amount = models.DecimalField( max_digits=10, decimal_places=2 )
    isconsumed = models.BooleanField()
    objects = GHManager()
    
class Subscription(GHModel):
    name = models.CharField( max_length=200, blank=True )
    user = models.ForeignKey( User, related_name='subscriptionuser+' )
    #txn = models.ForeignKey( Transaction, related_name='+', blank=True )
    pp_period3 = models.CharField( max_length=200, blank=True )
    pp_auth = models.CharField( max_length=200, blank=True )
    pp_charset = models.CharField( max_length=200, blank=True )
    pp_receiver_email = models.CharField( max_length=200, blank=True )
    pp_form_charset = models.CharField( max_length=200, blank=True )
    pp_item_number = models.CharField( max_length=200, blank=True )
    pp_payer_email = models.CharField( max_length=200, blank=True )
    pp_recurring = models.CharField( max_length=200, blank=True )
    pp_last_name = models.CharField( max_length=200, blank=True )
    pp_amount3 = models.CharField( max_length=200, blank=True )
    pp_mc_amount3 = models.CharField( max_length=200, blank=True )
    pp_subscr_id = models.CharField( max_length=200, blank=True )
    pp_mc_currency = models.CharField( max_length=200, blank=True )
    pp_txn_id = models.CharField( max_length=200, blank=True )
    pp_txn_type = models.CharField( max_length=200, blank=True )
    pp_btn_id = models.CharField( max_length=200, blank=True )
    pp_item_name = models.CharField( max_length=200, blank=True )
    pp_payer_status = models.CharField( max_length=200, blank=True )
    pp_reattempt = models.CharField( max_length=200, blank=True )
    pp_residence_country = models.CharField( max_length=200, blank=True )
    pp_business = models.CharField( max_length=200, blank=True )
    pp_subscr_date = models.CharField( max_length=200, blank=True )
    pp_payer_id = models.CharField( max_length=200, blank=True )
    pp_first_name = models.CharField( max_length=200, blank=True )
    pp_username = models.CharField( max_length=200, blank=True )
    pp_password = models.CharField( max_length=200, blank=True )
    notes = models.CharField( max_length=2000, blank=True )
    objects = GHManager()

