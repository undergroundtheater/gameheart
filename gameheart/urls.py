# gameheart.urls
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
#from paypay.standard.ipn import urls
from gameheart.entities import views
from gameheart.entities import forms

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gameheart.views.home', name='home'),
    # url(r'^gameheart/', include('gameheart.foo.urls')),
    url(r'^test/', views.test, name='test'),

    # Home page redirect

    url(r'$', RedirectView.as_view(url='/portal/')),
    
    # ADMIN
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # USER VIEWS
    url(r'^login/', views.UserLoginView, name='Login'),
    url(r'^logout/', views.UserLogoutView, name='Logout'),
    url(r'^terms/', views.UserTermsView, name='Terms'),
    url(r'^users/new/', views.UserCreateView, name='UserCreate'),
    url(r'^users/index/', views.UserIndexView, kwargs=dict(nform=forms.UserForm), name='UserIndex'),
    url(r'^users/detail/(?P<pkid>\d+)/$', views.UserDetailView, name='UserDetail'),
    url(r'^users/reset/(?P<pkid>\d+)/$', views.UserResetView, name='UserReset'),
    url(r'^account/detail/', views.UserAccountView, name='Account'),
    url(r'^account/password/', views.UserPasswordView, name='UserPassword'),

    # PORTAL
    url(r'^portal/', views.Portal, name='Portal'),
    url(r'^account/favorites/index/', views.UserFavoriteView, name='UserFavorites'),

### ##Create Views## ###
    # Chapter Type
    url(r'^types/chapters/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.ChapterTypeForm), name='ChapterTypeCreateView'),

    # Chapter
    url(r'^chapters/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.ChapterForm), name='ChapterCreateView'),
    
    # Event
    url(r'^chapters/events/new', views.FlexFormCreateView, kwargs=dict(nform=forms.EventForm), name='EventCreateView'),

    # Sign-in
    url(r'^signin/', views.AttendanceCreateView, name='AttendanceCreateView'),

    # Chapter Address
    url(r'^chapters/addresses/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.ChapterAddressForm), name='ChapterAddressCreateView'),

    # Staff Type
    url(r'^types/staff/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.StaffTypeForm), name='StaffTypeCreateView'),

    # Event
    url(r'^chapters/events/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.EventForm), name='EventCreateView'),
    
    # Character Type
    url(r'^types/characters/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.CharacterTypeForm), name='CharacterTypeCreateView'),

    # Character
    url(r'^characters/new/', views.CharacterCreateView, name='CharacterCreateView'),

    # Trait Type
    url(r'^types/traits/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.TraitTypeForm), name='TraitTypeCreateView'),

    # Trait
    url(r'^traits/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.TraitForm), name='TraitCreateView'),
 
    # Character Owner
    url(r'^characterowners/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.CharacterOwnerForm), name='CharacterOwnerCreateView'),

    # Note
    url(r'^notes/new/', views.NoteCreateView, name='NoteCreateView'),
    
### ## Indexes ## ###
    # ChapterTypes
    url(r'^types/chapters/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.ChapterTypeForm), name='ChapterTypeIndex'),
  
    # Chapters
    url(r'^chapters/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.ChapterForm), name='ChapterIndex'),
  
    # Chapters ST Index
    url(r'^chapters/stindex/', views.STChapterIndexView, kwargs=dict(nform=forms.ChapterForm), name='ChapterIndex'),
  
    # Chapter Addresses
    url(r'^chapters/addresses/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.ChapterAddressForm), name='ChapterAddressIndex'),

    # Event
    url(r'^chapters/events/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.EventForm), name='EventIndex'),

    # Staff Type
    url(r'^types/staff/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.StaffTypeForm), name='StaffTypeIndex'),

    # Character Types
    url(r'^types/characters/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.CharacterTypeForm), name='CharacterTypeIndex'),

    # Character Index
    url(r'^characters/index/', views.CharacterIndexView, kwargs=dict(nviewtype='owner'), name='CharacterIndex'),
    #url(r'^notes/index/(?P<ntagname>\w+)/', views.NoteIndexView, name='NoteIndex'),

    # Admin Character Index
    url(r'^director/characters/index/', views.CharacterIndexView, kwargs=dict(nviewtype='director'), name='CharacterIndex'),

    # ST Characters
    url(r'^characters/stindex/', views.CharacterIndexView, kwargs=dict(nviewtype='st'), name='CharacterIndex'),
    
    # User Favorites
    url(r'^account/favorites/users/index/', views.FavoriteIndexView, kwargs=dict(nform=forms.FavoriteUserForm), name='FavoriteUserIndex'),
    
    # Chapter Favorites
    url(r'^account/favorites/chapters/index/', views.FavoriteIndexView, kwargs=dict(nform=forms.FavoriteChapterForm), name='FavoriteChapterIndex'),
    
    # Character Favorites
    url(r'^account/favorites/characters/index/', views.FavoriteIndexView, kwargs=dict(nform=forms.FavoriteCharacterForm), name='FavoriteCharacterIndex'),
     
    # Trait Types
    url(r'^types/traits/index/', views.FlexFormIndexView, kwargs=dict(nform=forms.TraitTypeForm), name='TraitTypeIndex'),

    # Traits
    url(r'^traits/index/', views.TraitIndexView, kwargs=dict(nform=forms.TraitForm), name='TraitIndex'),

    # Notes    
    url(r'^notes/index/(?P<ntagname>\w+)/', views.NoteIndexView, name='NoteIndex'),

    # Vocabulary
    url(r'^vocabulary/index/', views.VocabularyIndexView, name='VocabularyIndex'),
    
### ## Detail Views ## ###
    # Chapter Type Detail
    url(r'^types/chapters/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.ChapterTypeForm), name='ChapterTypeDetail'),
    
    # Chapter Detail
    url(r'^chapters/(?P<pkid>\d+)/$', views.FlexFormDetailViewLinked, kwargs=dict(nform=forms.ChapterForm, ntemplate='flexdetailviewlinked.html'), name='ChapterDetail'),

    # Chapter Address Detail
    url(r'^chapters/addresses/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.ChapterAddressForm), name='ChapterAddressDetail'),
   
    # Event
    url(r'^chapters/events/(?P<pkid>\d+)/$', views.EventDetailView, name='EventDetail'),

    # Staff Type Detail
    url(r'^types/staff/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.StaffTypeForm), name='StaffTypeDetail'),
 
    # Character Type Detail
    url(r'^types/characters/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.CharacterTypeForm), name='CharacterTypeDetail'),
    
    # Character Trait Detail
    url(r'^characters/traits/(?P<pkid>\d+)/$', views.CharacterTraitDetailView, name='CharacterTraitDetail'),
    
    # Character Detail
    url(r'^characters/(?P<pkid>\d+)/$', views.CharacterDetailView, kwargs=dict(nform=forms.CharacterForm), name='CharacterDetail'),

    # Character Favorites
    url(r'^account/favorites/characters/(?P<pkid>\d+)/', views.FlexFormDetailView, kwargs=dict(nform=forms.CharacterForm), name='FavoriteCharacter'),
     
    # Trait Type Detail
    url(r'^types/traits/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.TraitTypeForm), name='TraitTypeDetail'),
    
    # Trait Detail
    url(r'^traits/(?P<pkid>\d+)/$', views.FlexFormDetailView, kwargs=dict(nform=forms.TraitForm), name='TraitDetail'),
   
    # Note Detail 
    url(r'^notes/(?P<pkid>\d+)/$', views.NoteDetailView, name='NoteDetail'),

### # Characters # ###

    ## Character Sheet
    url(r'^characters/(?P<pkid>\d+)/spendxp/', views.CharacterTraitSubmitView, name='CharacterTraitSubmit'),

    url(r'^characters/(?P<pkid>\d+)/creator/', views.CharacterCreatorView, name='CharacterCreator'),

    url(r'^characters/(?P<pkid>\d+)/upgrade/', views.CharacterUpgradeView, name='CharacterUpgrade'),

    url(r'^characters/(?P<pkid>\d+)/gridtime/(?P<ndate>\d+)/(?P<ntime>\d+)/', views.CharacterSheetGrid2, name='CharacterSheetGrid'),

    url(r'^characters/(?P<pkid>\d+)/grid/$', views.CharacterSheetGrid2, kwargs=dict(nformat='grid'), name='CharacterSheetGrid'),

    url(r'^characters/(?P<pkid>\d+)/print/', views.CharacterSheetGrid2, kwargs=dict(nformat='print'), name='CharacterSheetPrint'),

    url(r'^characters/(?P<pkid>\d+)/test/', views.CharacterSheetGrid2, kwargs=dict(nformat='test'), name='CharacterSheetTest'),

    url(r'^chapters/sheets/', views.CharacterSheetApprovalView, name='CharacterSheetApproval'),

    url(r'^chapters/(?P<pkid>\d+)/printall', views.CharacterSheetPrintall, name='CharacterSheetPrintall'),

    url(r'^characters/(?P<pkid>\d+)/pendingsheet/', views.PendingSheetView, name='PendingSheet'),

    url(r'^characters/(?P<pkid>\d+)/calcxp/', views.CharacterXPView, name='CharacterXP'),

    url(r'^characters/(?P<pkid>\d+)/charinfo/', views.CharacterInfoOnlyView, name='CharacterInfoOnly'),

    url(r'^characters/(?P<pkid>\d+)/fix/', views.CharacterFixView, name='CharacterFix'),

    # Character Removal
    url(r'^characters/(?P<pkid>\d+)/hide/', views.CharacterHideView, name='CharacterHide'),
    url(r'^characters/(?P<pkid>\d+)/kill/', views.CharacterKillView, name='CharacterKill'),
    url(r'^characters/(?P<pkid>\d+)/shelf/', views.CharacterShelfView, name='CharacterShelf'),

### Payments ###
    url(r'^account/upgrade/(?P<nitem>\w+)/', views.AccountUpgradeView, name='AccountUpgrade'),

    url(r'^account/upgradesuccess/', views.AccountUpgradeSuccessView, name='AccountUpgrageSuccess'),

    url(r'^account/upgradecancel/', views.AccountUpgradeCancelView, name='AccountUpgradeCancel'),

    url(r'^account/thankyou/', views.AccountUpgradeThankYou, name='AccountUpgradeThankYou'),

    url(r'^payments/notify/', views.PaypalPaymentNotify, name='PaypalPaymentNotify'),

    # Subscriptions
    url(r'^subscriptions/user/(?P<pkid>\d+)/', views.FlexFormIndexView, kwargs=dict(nform=forms.SubscriptionForm), name='SubscriptionIndex'),
    url(r'^subscriptions/new/', views.FlexFormCreateView, kwargs=dict(nform=forms.SubscriptionForm), name='Subscription'),
    url(r'^subscriptions/(?P<pkid>\d+)/', views.FlexFormDetailView, kwargs=dict(nform=forms.SubscriptionForm), name='SubscriptionDetail'),
    url(r'^subscriptions/index/', views.SubscriptionIndexView, name='SubscriptionDetail'),

## Static Content ##
    url(r'^static/(?P<nfile>\w+)', views.Static, name='Static'),

## AJAX ##
    url(r'^ajaxexample$', views.ajaxPing, name='AJAX Test'),
    url(r'^ajaxexample_json$', views.ajaxTest, name='AJAX'),
    
    url(r'^tests/ajaxatraits/', views.TestAjaxATraits, name='TestAjaxATraits'),
    url(r'^ajax/atraits/', views.ajaxATraits, name='AJAXATraits'),
    url(r'^ajax/atraittype/', views.ajaxATraitType, name='AJAXATraitType'),
    url(r'^ajax/atraitsbytype/', views.ajaxATraitsByType, name='AJAXATraitsByType'),

## Execute Functions ##
    url(r'^fixall/', views.ExecuteView, kwargs=dict(nfunction='fixall'), name='ExecuteFixall')
	
## End URLS
)

