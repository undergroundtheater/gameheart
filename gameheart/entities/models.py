#gameheart.entities.models

from datetime import datetime
from django.db import models
from django.db.models import Q
from django.db import DEFAULT_DB_ALIAS
from django.contrib.auth.models import User

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
            date = datetime.now()
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
            date = datetime.now()
        return self.filter(Q(dateactive=None)|Q(dateactive__lte=date)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=date)).filter(Q(dateremoved=None)|Q(dateremoved__gte=date))
    def sheetonly(self,date=None):
        if date == None:
            date = datetime.now()
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

def install():
    donothing = 1
    return False
'''
    # Create objects here using Django ORM
    model = User.objects.get(username='treetop')
    # Users
    UserProfile(user=model, name='Treetop', isadmin=1).save()
    #model = User.objects.create_user('jutmike2000@gmail.com', 'justmike2000@gmail.com', 'mileusnich')
    #UserProfile(user=model, name='Miles', isadmin=1).save()
    model = User.objects.create_user('miagardener@gmail.com', 'miagardener@gmail.com', 'gerber')
    UserProfile(user=model, name='Meredith', isadmin=1).save()
    model = User.objects.create_user('bobspircoff@gmail.com', 'bobspircoff@gmail.com', 'spircoff')
    UserProfile(user=model, name='Bob', isadmin=1).save()
    model = User.objects.create_user('mftomasek@gmail.com', 'mftomasek@gmail.com', 'tomasek')
    UserProfile(user=model, name='Hollywood', isadmin=1).save()
    model = User.objects.create_user('walker27067@gmail.com', 'walker27067@gmail.com', 'walker')
    UserProfile(user=model, name='Criss', isadmin=1).save()
    #model = User.objects.create_user('storyteller@example.com', 'storyteller@example.com', 'test123')
    #UserProfile(user=model, name='ST Test', isadmin=0).save()
    #model = User.objects.create_user('patron@example.com', 'patron@example.com', 'test123')
    #UserProfile(user=model, name='Patron Test', isadmin=0).save()
    # Vocabulary
    Vocabulary(name='User', displayname='Patron', displayplural='Patrons').save()
    Vocabulary(name='ChapterType', displayname='Setting', displayplural='Settings').save()
    Vocabulary(name='Chapter', displayname='Troupe', displayplural='Troupes').save()
    Vocabulary(name='ChapterAddress', displayname='Site', displayplural='Sites').save()
    Vocabulary(name='StaffType', displayname='Staff Type', displayplural='Staff Types').save()
    Vocabulary(name='Staff', displayname='Staff', displayplural='Staff').save()
    Vocabulary(name='Event', displayname='Game', displayplural='Games').save()
    Vocabulary(name='CharacterType', displayname='Character Type', displayplural='Character Types').save()
    Vocabulary(name='Character', displayname='Character', displayplural='Characters').save()
    Vocabulary(name='TraitType', displayname='Trait Type', displayplural='Trait Types').save()
    Vocabulary(name='Trait', displayname='Trait', displayplural='Traits').save()
    Vocabulary(name='Note', displayname='Note', displayplural='Notes').save()
    Vocabulary(name='Favorite', displayname='Favorite', displayplural='Favorites').save()
    Vocabulary(name='Poll', displayname='Vote', displayplural='Votes').save()
    Vocabulary(name='Subscription', displayname='Subscription', displayplural='Subscriptions').save()
    Vocabulary(name='Upgrade', displayname='donate', displayplural='Donations').save()
    Vocabulary(name='DBVersion', displayname='0.00.03', displayplural='0.00.03').save()
    
    # Chapters(Settings)
    model = ChapterType(name='Camarilla',description='Also includes Anarch games.')
    model.save()
    model2 = Chapter(type=model, name='Test Cam')
    model2.save()
    ChapterAddress(chapter=model2, name='My House', address1='7552 Benton Dr', city='Frankfort', state='IL', zip='60423').save()
    model = ChapterType(name='Sabbat')
    model.save()
    model2 = Chapter(type=model, name='Test Sabbat')
    model2.save()
    ChapterAddress(chapter=model2, name='My House', address1='7552 Benton Dr', city='Frankfort', state='IL', zip='60423').save()
    # Character Types
    CharacterType(name='Vampire').save()
    # Staff Types
    StaffType(name='DST', isapprover=True, isdirector=True).save()
    StaffType(name='ST', isapprover=True).save()
    StaffType(name='Narrator').save()
    StaffType(name='Admin', isapprover=True).save()
    # Clans
    clantype = TraitType(name='Clan', onepercharacter=True)
    clantype.save()
    bltype = TraitType(name='Bloodline', aggregate=1)
    bltype.save()
    model = Trait(type=clantype, name='Assamite', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Vizier', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Sorcerer', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Brujah', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='True Brujah', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Settite', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Tlicique', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Vipers', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Gangrel', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Coyote', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Noiad', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Ahrimane', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Giovanni', level=0)
    model.save()
    model = Trait(type=clantype, name='Lasombra', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Kiasyd', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Malkavian', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Ananke', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Knights of the Moon', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Nosferatu', level=0)
    model.save()
    model = Trait(type=clantype, name='Tremere', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Telyav', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Tzimisce', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Carpathian', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    blmodel = Trait(type=bltype, name='Koldun', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Ventrue', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='Crusader', level=0)
    blmodel.save()
    blmodel.cotraits.add(model.id)
    model = Trait(type=clantype, name='Caitiff', level=0)
    model.save()
    blmodel = Trait(type=bltype, name='None', level=0)
    blmodel.save()
    # Traits
    model = TraitType(name='Archetype', onepercharacter=True)
    model.save()
    Trait(type=model, name='Bravo', level=0).save()
    Trait(type=model, name='Architect', level=0).save()
    model = TraitType(name='Temper', aggregate=1, xpcost1=10, xpcost2=10, xpcost3=10, xpcost4=10, xpcost5=10)
    model.save()
    Trait(type=model, name='Blood', level=1).save()
    Trait(type=model, name='Willpower', level=1).save()
    Trait(type=model, name='Morality', level=1).save()
    Trait(type=model, name='Humanity', level=1).save()
    model = TraitType(name='Attribute', aggregate=1, xpcost1=3, xpcost2=3, xpcost3=3, xpcost4=3, xpcost5=3)
    model.save()
    Trait(type=model, name='Physical', level=0).save()
    Trait(type=model, name='Mental', level=0).save()
    Trait(type=model, name='Social', level=0).save()
    model = TraitType(name='Physical Focus')
    model.save()
    Trait(type=model, name='Strength', level=0).save()
    Trait(type=model, name='Dexterity', level=0).save()
    Trait(type=model, name='Stamina', level=0).save()
    model = TraitType(name='Social Focus')
    model.save()
    Trait(type=model, name='Charisma', level=0).save()
    Trait(type=model, name='Manipulation', level=0).save()
    Trait(type=model, name='Appearance', level=0).save()
    model = TraitType(name='Mental Focus')
    model.save()
    Trait(type=model, name='Perception', level=0).save()
    Trait(type=model, name='Intelligence', level=0).save()
    Trait(type=model, name='Wits', level=0).save()
    model = TraitType(name='Skill', aggregate=1, multiplyxp=True, xpcost1=1, xpcost2=2, xpcost3=2, xpcost4=2, xpcost5=2)
    model.save()
    Trait(type=model, name='Academics', level=1).save()
    Trait(type=model, name='Animal Ken', level=1).save()
    Trait(type=model, name='Athletics', level=1).save()
    Trait(type=model, name='Awareness', level=1).save()
    Trait(type=model, name='Brawl', level=1).save()
    Trait(type=model, name='Computer', level=1).save()
    Trait(type=model, name='Dodge', level=1).save()
    Trait(type=model, name='Drive', level=1).save()
    Trait(type=model, name='Empathy', level=1).save()
    Trait(type=model, name='Firearms', level=1).save()
    Trait(type=model, name='Intimidation', level=1).save()
    Trait(type=model, name='Investigation', level=1).save()
    Trait(type=model, name='Leadership', level=1).save()
    Trait(type=model, name='Linguistics', level=1).save()
    Trait(type=model, name='Lore', level=1).save()
    Trait(type=model, name='Medicine', level=1).save()
    Trait(type=model, name='Melee', level=1).save()
    Trait(type=model, name='Occult', level=1).save()
    Trait(type=model, name='Security', level=1).save()
    Trait(type=model, name='Stealth', level=1).save()
    Trait(type=model, name='Streetwise', level=1).save()
    Trait(type=model, name='Subterfuge', level=1).save()
    Trait(type=model, name='Survival', level=1).save()
    model = TraitType(name='Background', aggregate=1, multiplyxp=True, xpcost1=2, xpcost2=2, xpcost3=2, xpcost4=2, xpcost5=2)
    model.save()
    Trait(type=model, name='Generation', level=1).save()
    Trait(type=model, name='Contacts', level=1).save()
    Trait(type=model, name='Allies', level=1).save()
    Trait(type=model, name='Mentor', level=1).save()
    model = TraitType(name='Discipline', aggregate=1, multiplyxp=True, xpcost1=3, xpcost2=3, xpcost3=3, xpcost4=3, xpcost5=3)
    model.save()
    Trait(type=model, name='Animalism', level=1).save()
    Trait(type=model, name='Auspex', level=1).save()
    Trait(type=model, name='Celerity', level=1).save()
    Trait(type=model, name='Dominate', level=1).save()
    Trait(type=model, name='Fortitude', level=1).save()
    Trait(type=model, name='Obfuscate', level=1).save()
    Trait(type=model, name='Potence', level=1).save()
    Trait(type=model, name='Presence', level=1).save()
    Trait(type=model, name='Quietus', level=1).save()
    Trait(type=model, name='Temporis', level=1).save()
    Trait(type=model, name='Serpentis', level=1).save()
    Trait(type=model, name='Protean', level=1).save()
    Trait(type=model, name='Obtenebration', level=1).save()
    Trait(type=model, name='Mythreceria', level=1).save()
    Trait(type=model, name='Vicissitude', level=1).save()
    Trait(type=model, name='Thaumaturgy: Path of Blood', level=1).save()
    Trait(type=model, name='Thaumaturgy: Path of Elemental Mastery', level=1).save()
    Trait(type=model, name='Thaumaturgy: Lure of Flame', level=1).save()
    Trait(type=model, name='Necromancy: Sepulchre Path', level=1).save()
    model = TraitType(name='In-Clan Discipline', aggregate=0, multiplyxp=False, xpcost1=0, xpcost2=0, xpcost3=0, xpcost4=0, xpcost5=0)
    model.save()
    Trait(type=model, name='Animalism', level=0).save()
    Trait(type=model, name='Auspex', level=0).save()
    Trait(type=model, name='Celerity', level=0).save()
    Trait(type=model, name='Dominate', level=0).save()
    Trait(type=model, name='Fortitude', level=0).save()
    Trait(type=model, name='Obfuscate', level=0).save()
    Trait(type=model, name='Potence', level=0).save()
    Trait(type=model, name='Presence', level=0).save()
    Trait(type=model, name='Quietus', level=0).save()
    Trait(type=model, name='Temporis', level=0).save()
    Trait(type=model, name='Serpentis', level=0).save()
    Trait(type=model, name='Protean', level=0).save()
    Trait(type=model, name='Obtenebration', level=0).save()
    Trait(type=model, name='Mythreceria', level=0).save()
    Trait(type=model, name='Vicissitude', level=0).save()
    Trait(type=model, name='Thaumaturgy: Path of Blood', level=0).save()
    Trait(type=model, name='Thaumaturgy: Path of Elemental Mastery', level=0).save()
    Trait(type=model, name='Thaumaturgy: Lure of Flame', level=0).save()
    Trait(type=model, name='Necromancy: Sepulchre Path', level=0).save()
    model = TraitType(name='Merit', multiplyxp=True, xpcost1=1, xpcost2=1, xpcost3=1, xpcost4=1, xpcost5=1)
    model.save()
    Trait(type=model, name='Common Sense', level=4).save()
    Trait(type=model, name='Danger Sense', level=2).save()
    Trait(type=model, name='Bloodline: Vizier', level=2, isadmin=True).save()
    model = TraitType(name='Flaw', multiplyxp=True, xpcost1=-1, xpcost2=-1, xpcost3=-1, xpcost4=-1, xpcost5=-1)
    model.save()
    Trait(type=model, name='Derrangement', level=3).save()
    Trait(type=model, name='Conspicuous Consumption', level=4).save()
    Trait(type=model, name='Big Head', level=2).save()
    model = TraitType(name='Status')
    model.save()
    Trait(type=model, name='Acknowledged', level=0).save()
    Trait(type=model, name='Respected', level=0).save()
    Trait(type=model, name='Knowledgeable', level=0).save()
    model = TraitType(name='State')
    model.save()
    Trait(type=model, name='New', level=0, isadmin=True).save()
    Trait(type=model, name='Pending', level=0, isadmin=True).save()
    Trait(type=model, name='Active', level=0, isadmin=True).save()
    Trait(type=model, name='Dead', level=0, isadmin=True).save()
    Trait(type=model, name='Shelved', level=0, isadmin=True).save()
    model = TraitType(name='Priority')
    model.save()
    Trait(type=model, name='Primary', level=0, isadmin=True).save()
    Trait(type=model, name='Secondary', level=0, isadmin=True).save()
    Trait(type=model, name='STC', level=0, isadmin=True).save()

    # Test Characters
    #numlist = [1,2,3,4,5]
    #chartype = CharacterType.objects.get(name='Vampire')
    #chapter = Chapter.objects.get(name='Test Cam Troupe')
    #for u in numlist:
    #    user = User.objects.get(pk=u)
    #    for c in numlist:
    #        if c == 1:
    #            isprimary=1
    #        else:
    #            isprimary=0
    #            isnew=1
    #        name = ''.join([user.username,' Character',str(c)])
    #        model = Character(type=chartype,chapter=chapter,name=name,isprimary=isprimary)
    #        model.save()
    #        CharacterOwner(user=user,character=model,iscontroller=True).save()
   ''' 
