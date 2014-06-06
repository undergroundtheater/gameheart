#gameheart.entities.forms

from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gameheart.entities.models import *
from gameheart.entities.helpers import *

class GHForm(forms.ModelForm):
    class Meta:
        abstract = True
    def __init__(self, user=None, *args, **kwargs):
        super(GHForm, self).__init__(*args, **kwargs)
        userinfo = getuserinfo(user)
        if not userinfo:
            admin = True
        else:
            admin = userinfo['isadmin']
        instance = kwargs.pop('instance',None)
        owned = isowned(instance,user)
        approver = isapprover(instance,user)
        if hasattr(self,'readonlyfields'):
            for field in self.readonlyfields:
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].widget.attrs['disabled'] = True
                self.fields[field].required = False
        if hasattr(self,'adminonlyfields') and admin == False:
            for field in self.adminonlyfields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].widget.attrs['disabled'] = True
        if hasattr(self,'isprivate'):
            if self.isprivate == True and owned == False and admin == False and instance:
                for field in self.Meta.fields:
                    self.fields[field].widget.attrs['readonly'] = True
                    self.fields[field].widget.attrs['disabled'] = True
        if hasattr(self,'ownedonlyfields') and owned == False:
            for field in self.ownedonlyfields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].widget.attrs['disabled'] = True
        if hasattr(self,'approveronlyfields') and approver == False:
            for field in self.approveronlyfields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].widget.attrs['disabled'] = True
        if hasattr(self,'hiddenfields'):
            for field in self.hiddenfields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].widget.attrs['disabled'] = True

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email',]
        widgets = {
            'password':forms.PasswordInput
        }
    isadmin = False
    isprivate = True
    mname = 'User'

class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
    buttons = [
        {'name':'xpspend','class':'button','id':'xpspend','value':'Spend XP','link':'spendxp/','isadmin':False,'isnew':False}]
    isadmin = False
    isprivate = False
    mname = 'User'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name','description']
    isadmin = False
    isprivate = False
    mname = 'User'

class UserDetailProfileForm(GHForm):
    class Meta:
        model = UserProfile
        fields = ['name','isadmin','description']
    adminonlyfields = ['isadmin']
    isadmin = False
    isprivate = False
    mname = 'User'

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password':forms.PasswordInput
        }
    isadmin = False
    isprivate = False
    mname = 'User'

class ChapterTypeForm(GHForm):
    class Meta:
        model = ChapterType
        fields = ['name', 'description','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name']
    sname = Vocabulary.objects.get(name='ChapterType').displayname
    surl = '/types/chapters/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = False
    mname = 'ChapterType'

class StaffTypeForm(GHForm):
    class Meta:
        model = StaffType
        fields = ['name', 'isapprover', 'isdirector', 'description','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry','isapprover', 'isdirector']
    ifields = ['name']
    sname = Vocabulary.objects.get(name='StaffType').displayname
    surl = '/types/staff/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = False
    mname = 'StaffType'

class StaffForm(GHForm):
    class Meta:
        model = Staff
        fields = ['user', 'type','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    lfield = 'chapter'
    sname = Vocabulary.objects.get(name='Staff').displayname
    surl = '/staff/'
    sheading = ''.join(['Add New ',sname])
    isadmin = False
    isprivate = False
    mname = 'Staff'
    def __init__(self, *args, **kwargs):
        super(StaffForm,self).__init__(*args, **kwargs)
        self.fields['user'].label = Vocabulary.objects.get(name='User').displayname

class ChapterForm(GHForm):
    class Meta:
        model = Chapter
        fields = ['name', 'type', 'description', 'dateactive', 'dateexpiry']
        exclude = []
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name', 'type']
    buttons = []
    lform = StaffForm
    sname = Vocabulary.objects.get(name='Chapter').displayname
    surl = '/chapters/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = True
    mname = 'Chapter'

class ChapterAddressForm(GHForm):
    class Meta:
        model = ChapterAddress
        fields = ['name', 'chapter', 'address1', 'address2', 'city', 'state', 'zip', 'dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name', 'chapter', 'city', 'state']
    sname = ''.join([Vocabulary.objects.get(name='ChapterAddress').displayname])
    surl = '/chapters/addresses/'
    sheading = ''.join(['Add New ',sname])
    isadmin = False
    isprivate = False
    mname = 'ChapterAddress'
    def __init__(self, *args, **kwargs):
        super(ChapterAddressForm,self).__init__(*args, **kwargs)
        self.fields['chapter'].label = Vocabulary.objects.get(name='Chapter').displayname

class CharacterTypeForm(GHForm):
    class Meta:
        model = CharacterType
        fields = ['name', 'description','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name']
    sname = Vocabulary.objects.get(name='CharacterType').displayname
    surl = '/types/characters/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = False
    mname = 'CharacterType'

class CharacterOwnerForm(GHForm):
    class Meta:
        model = CharacterOwner
        fields = ['user','iscontroller','dateactive','dateexpiry']
    adminonlyfields = ['iscontroller','dateactive','dateexpiry']
    lfield = 'character'
    sname = 'Character Owner'
    surl = '/characters/owners/'
    sheading = 'Assign Character to User'
    isadmin = False
    isprivate = False
    mname = 'CharacterOwner'

class CharacterForm(GHForm):
    class Meta:
        model = Character
        fields = ['name', 'type', 'chapter', 'public_description', 'private_description','dateactive','dateexpiry']
        exclude = []
    adminonlyfields = ['dateactive','dateexpiry']
    ownedonlyfields = ['type','private_description']
    ifields = ['name', 'type', 'chapter']
    directorfields = ['name', 'type', 'chapter', 'isprimary', 'isnew', 'public_description', 'private_description']
    lform = CharacterOwnerForm
    sname = Vocabulary.objects.get(name='Character').displayname
    surl = '/characters/'
    sheading = ''.join(['Add New ',sname])
    buttons = [
        {'name':'sheet','class':'button','id':'sheet','value':'View Sheet','link':'grid/','isadmin':False,'isnew':False,'check':False,'newtab':False,'controlleronly':False,'directoronly':False},
        {'name':'print','class':'button','id':'print','value':'Print','link':'print/','isadmin':False,'isnew':False,'check':False,'newtab':True,'controlleronly':False,'directoronly':False},
        {'name':'xplog','class':'button','id':'xplog','value':'XP Log','link':'calcxp/','isadmin':False,'isnew':False,'check':False,'newtab':False,'controlleronly':False,'directoronly':False},
        #{'name':'fix','class':'button','id':'fix','value':'Fix','link':'fix/','isadmin':False,'isnew':False,'check':False,'newtab':False,'controlleronly':False,'directoronly':True},
        {'name':'labels','class':'button','id':'labels','value':'Labels','link':'traits/labels/','isadmin':False,'isnew':False,'check':False,'newtab':False,'controlleronly':False,'directoronly':True},
        {'name':'remove','class':'button','id':'remove','value':'Remove','link':'hide/','isadmin':False,'isnew':True,'check':True,'newtab':False,'controlleronly':True,'directoronly':True}
    ]
    isadmin = False
    isprivate = True
    mname = 'Character'
    def __init__(self, *args, **kwargs):
        super(CharacterForm,self).__init__(*args, **kwargs)
        self.fields['chapter'].label = Vocabulary.objects.get(name='Chapter').displayname

class TraitTypeForm(GHForm):
    charactertypes = forms.ModelMultipleChoiceField(queryset=CharacterType.objects.activeonly(),widget=forms.CheckboxSelectMultiple(),required=False)
    chaptertypes = forms.ModelMultipleChoiceField(queryset=ChapterType.objects.activeonly(),widget=forms.CheckboxSelectMultiple(),required=False)
    class Meta:
        model = TraitType
        fields = ['name', 'aggregate', 'onepercharacter', 'multiplyxp', 'labelable', 'xpcost1','xpcost2','xpcost3','xpcost4','xpcost5','cotrait','availtocontroller','availtoapprover','availtodirector','description', 'charactertypes', 'chaptertypes', 'dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name']
    sname = Vocabulary.objects.get(name='TraitType').displayname
    surl = '/types/traits/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = False
    mname = 'TraitType'
    def __init__(self, *args, **kwargs):
        super(TraitTypeForm,self).__init__(*args, **kwargs)
        self.fields['labelable'].label = 'Can be Labeled'

class TraitForm(GHForm):
    charactertypes = forms.ModelMultipleChoiceField(queryset=CharacterType.objects.activeonly(),widget=forms.CheckboxSelectMultiple(),required=False)
    chaptertypes = forms.ModelMultipleChoiceField(queryset=ChapterType.objects.activeonly(),widget=forms.CheckboxSelectMultiple(),required=False)
    cotraits = forms.ModelMultipleChoiceField(queryset=Trait.objects.cotraits(),widget=widgets.FilteredSelectMultiple(verbose_name='Required Traits',is_stacked=False),required=False)
    bantraits = forms.ModelMultipleChoiceField(queryset=Trait.objects.cotraits(),widget=widgets.FilteredSelectMultiple(verbose_name='Banned Traits',is_stacked=False),required=False)
    addtraits = forms.ModelMultipleChoiceField(queryset=Trait.objects.cotraits(),widget=widgets.FilteredSelectMultiple(verbose_name='Add Traits',is_stacked=False),required=False)
    class Meta:
        model = Trait
        fields = ['name', 'type', 'level', 'isadmin', 'renamable', 'description', 'charactertypes', 'chaptertypes', 'cotraits','bantraits','addtraits','dateactive','dateexpiry']
    adminonlyfields = ['isadmin', 'dateactive','dateexpiry']
    ifields = ['type', 'name']
    fieldlist = ['id', 'name', 'level', 'xpcost', 'bpcost', 'description']
    sname = Vocabulary.objects.get(name='Trait').displayname
    surl = '/traits/'
    sheading = ''.join(['Add New ',sname])
    isadmin = True
    isprivate = False
    mname = 'Trait'
    def __init__(self, *args, **kwargs):
        super(TraitForm,self).__init__(*args, **kwargs)
        self.fields['renamable'].label = 'Can be Ranamed'
        Trait.__unicode__ = Trait.cotrait_label

class CharacterTraitForm(GHForm):
    class Meta:
        model = CharacterTrait
        fields = ['character', 'trait', 'iscreation', 'isfree', 'authorizedby', 'dateauthorized', 'dateremoved', 'dateactive','dateexpiry']
    adminonlyfields = ['authorizedby','dateauthorized','dateactive','dateexpiry']
    approveronlyfields = ['iscreation','isfree','authorizedby','dateauthorized','dateremoved','dateactive','dateexpiry']
    readonlyfields = ['character','trait']
    sname = 'Character Trait'
    surl = '/characters/traits/'
    sheading = 'Add New Trait to Character'
    sredirect = 'user_index'
    isadmin = False
    isprivate = False
    mname = 'CharacterTrait'

class AttendanceForm(GHForm):
    class Meta:
        model = Attendance
        fields = ['user','character','event','xpawarded','authorizedby']
    adminonlyfields = ['user','event','authorizedby']
    hiddenfields = ['user','event','authorizedby']
    fieldlabels = [Vocabulary.objects.get(name='User').displayname,Vocabulary.objects.get(name='Character').displayname,Vocabulary.objects.get(name='Event').displayname,'xpawarded','authorizedby']
    lfield = 'event'
    sname = 'Attendance'
    surl = '/chapterss/events/attendance/'
    sheading = ''.join(['Sign in to ',Vocabulary.objects.get(name='Event').displayname])
    isadmin = False
    isprivate = False
    mname = 'Attendance'
    def __init__(self, *args, **kwargs):
        super(AttendanceForm,self).__init__(*args, **kwargs)
        self.fields['user'].label = Vocabulary.objects.get(name='User').displayname
        self.fields['event'].label = Vocabulary.objects.get(name='Event').displayname

class AttendanceGameForm(GHForm):
    class Meta:
        model = Attendance
        fields = ['user','character','event','xpawarded','authorizedby']
    adminonlyfields = ['user','event','authorizedby']
    hiddenfields = ['user','event','authorizedby']
    fieldlabels = [Vocabulary.objects.get(name='User').displayname,Vocabulary.objects.get(name='Character').displayname,Vocabulary.objects.get(name='Event').displayname,'xpawarded','authorizedby']
    lfield = 'event'
    sname = 'Attendance'
    surl = '//'
    sheading = ''.join(['Sign in to ',Vocabulary.objects.get(name='Event').displayname])
    isadmin = False
    isprivate = False
    mname = 'Attendance'
    def __init__(self, *args, **kwargs):
        super(AttendanceGameForm,self).__init__(*args, **kwargs)
        self.fields['user'].label = Vocabulary.objects.get(name='User').displayname
        self.fields['event'].label = Vocabulary.objects.get(name='Event').displayname

class EventForm(GHForm):
    class Meta:
        model = Event
        fields = ['name', 'chapter', 'chapteraddress', 'dateheld','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    ifields = ['name', 'chapter']
    #approveronlyfields = ['name', 'chapter', 'chapteraddress', 'dateheld']
    lform = AttendanceForm
    sname = Vocabulary.objects.get(name='Event').displayname
    surl = '/chapters/events/'
    sheading = ''.join(['Add New ',sname])
    isadmin = False
    isprivate = False
    mname = 'Event'
    buttons = []
    def __init__(self, *args, **kwargs):
        super(EventForm,self).__init__(*args, **kwargs)
        self.fields['chapter'].label = Vocabulary.objects.get(name='Chapter').displayname
        self.fields['chapteraddress'].label = Vocabulary.objects.get(name='ChapterAddress').displayname

class NoteForm(GHForm):
    class Meta:
        model = Note
        fields = ['subject', 'body','character','chapter','trait','traitlevel','stafftype','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    sname = Vocabulary.objects.get(name='Note').displayname
    surl = '/notes/'
    sheading = ''.join(['Add New ',sname])
    isadmin = False
    isprivate = False
    mname = 'Note'

class NoteTagForm(GHForm):
    class Meta:
        model = NoteTag
        fields = ['tag','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    sname = 'Note'
    surl = '/notes/tags/'
    sheading = 'Add New Note Tag'
    isadmin = False
    isprivate = False
    mname = 'NoteTag'

class FavoriteUserForm(GHForm):
    class Meta:
        model = FavoriteUser
        fields = ['favoriteuser']
    adminonlyfields = []
    fkmodel = UserProfile
    fkfield = 'favoriteuser'
    sname = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='User').displayname])
    surl = '/account/favorites/users/'
    sheading = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='User').displayplural])
    isadmin = False
    isprivate = False
    lform = UserForm
    mname = 'FavoriteUser'
    def __init__(self, *args, **kwargs):
        super(FavoriteUserForm,self).__init__(*args, **kwargs)
        self.fields['favoriteuser'].label = ''.join([Vocabulary.objects.get(name='Favorite').displayname,' ',Vocabulary.objects.get(name='User').displayname])

class FavoriteChapterForm(GHForm):
    class Meta:
        model = FavoriteChapter
        fields = ['favoritechapter']
    adminonlyfields = []
    fkmodel = Chapter
    fkfield = 'favoritechapter'
    sname = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='Chapter').displayname])
    surl = '/account/favorites/chapters/'
    sheading = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='Chapter').displayplural])
    isadmin = False
    isprivate = False
    lform = ChapterForm
    mname = 'FavoriteChapter'
    def __init__(self, *args, **kwargs):
        super(FavoriteChapterForm,self).__init__(*args, **kwargs)
        self.fields['favoritechapter'].label = ''.join([Vocabulary.objects.get(name='Favorite').displayname,' ',Vocabulary.objects.get(name='Chapter').displayname])

class FavoriteCharacterForm(GHForm):
    class Meta:
        model = FavoriteCharacter
        fields = ['favoritecharacter']
    adminonlyfields = []
    fkmodel = Character
    fkfield = 'favoritecharacter'
    sname = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='Character').displayname])
    surl = '/account/favorites/characters/'
    sheading = ''.join([Vocabulary.objects.get(name='Favorite').displayname, ' ', Vocabulary.objects.get(name='Character').displayplural])
    isadmin = False
    isprivate = False
    lform = CharacterForm
    mname = 'FavoriteCharacter'
    def __init__(self, *args, **kwargs):
        super(FavoriteCharacterForm,self).__init__(*args, **kwargs)
        self.fields['favoritecharacter'].label = ''.join([Vocabulary.objects.get(name='Favorite').displayname,' ',Vocabulary.objects.get(name='Character').displayname])

class VocabularyForm(GHForm):
    class Meta:
        model = Vocabulary
        fields = ['displayname','displayplural']
    adminonlyfields = ['displayname', 'displayplural']
    sname = 'Vocabulary'
    surl = '/vocabulary/'
    sheading = 'Vocabulary'
    isadmin = False
    isprivate = False
    mname = 'Vocabulary'

class TransactionForm(GHForm):
    class Meta:
        model = Transaction
        fields = ['user','txnid','amount','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    isadmin = False
    isprivate = False
    mname = 'Transaction'

class SubscriptionForm(GHForm):
    class Meta:
        model = Subscription
        fields = ['user','name','pp_period3','pp_auth','pp_charset','pp_receiver_email','pp_amount3','pp_form_charset','pp_item_number','pp_payer_email','pp_recurring','pp_last_name','pp_payer_id','pp_mc_amount3','pp_subscr_id','pp_mc_currency','pp_txn_id','pp_txn_type','pp_btn_id','pp_item_name','pp_payer_status','pp_password','pp_reattempt','pp_residence_country','pp_business','pp_subscr_date','pp_first_name','notes','dateactive','dateexpiry']
    adminonlyfields = ['dateactive','dateexpiry']
    surl = '/subscriptions/'
    isadmin = False
    isprivate = False
    mname = 'Subscription'

