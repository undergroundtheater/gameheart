#gameheart.entities.admin

from django.contrib import admin
from django.contrib.auth.models import User
from gameheart.entities.models import *

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name','user','acceptedterms',]})
    ]

class CharacterTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name',]}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]

class TraitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'type', 'level', 'isadmin', 'renamable', 'charactertypes', 'chaptertypes', 'description',]}),
        ('Cotraits',{'fields':['cotraits','bantraits','addtraits'], 'classes': ['collapse',]}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    filter_horizontal = ('cotraits','bantraits','addtraits',)
    list_display = ['name', 'type']

class TraitInline(admin.TabularInline):
    model = Trait
    fieldsets = [
        (None,     {'fields': ['name', 'isadmin', 'renamable', 'level', 'charactertypes','chaptertypes','cotraits','bantraits','addtraits']}),
    ]
    filter_horizontal = ('cotraits','bantraits','addtraits',)
    extra = 10

class TraitTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'aggregate', 'onepercharacter', 'multiplyxp', 'labelable', 'availtocontroller','availtoapprover','availtodirector','xpcost1', 'xpcost2', 'xpcost3', 'xpcost4', 'xpcost5', 'charactertypes','chaptertypes','description']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    inlines = [TraitInline]

class CharacterOwnerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['character', 'user', 'iscontroller',]}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['character', 'user',]

class CharacterOwnerInline(admin.TabularInline):
    model = CharacterOwner
    fieldsets = [
        (None,     {'fields': ['character', 'user', 'iscontroller',]}),
    ]
    extra = 1

class CharacterTraitAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['character', 'trait','iscreation']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['character', 'trait', 'iscreation', 'authorizedby', 'dateauthorized', 'dateactive', 'dateexpiry']

class CharacterTraitInline(admin.TabularInline):
    model = CharacterTrait
    fieldsets = [
        (None,     {'fields': ['character', 'trait', 'iscreation', 'authorizedby','dateactive','dateexpiry']})
    ]
    extra = 10

class TraitLabelInline(admin.TabularInline):
    model = TraitLabel
    fieldsets = [
        (None,     {'fields': ['character', 'trait', 'label', 'authorizedby', 'dateactive', 'dateexpiry']})
    ]
    extra = 1

class CharacterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'type', 'chapter', 'public_description', 'private_description',]}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['name', 'type', 'chapter',]
    inlines = [CharacterOwnerInline, CharacterTraitInline, TraitLabelInline]
    search_fields = ['name',]

class DiscountAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['charactertrait', 'authorizedby', 'xpdiscount', 'bpdiscount', 'reason']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['charactertrait', 'authorizedby', 'xpdiscount', 'bpdiscount']

class StaffTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'description']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['name', 'description']

class StaffAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['chapter', 'user', 'type']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['chapter', 'user', 'type']

class StaffInline(admin.TabularInline):
    model = Staff
    fieldsets = [
        (None,     {'fields': ['chapter', 'user', 'type']}),
    ]
    extra = 3

class ChapterTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'description']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]

class ChapterAddressInline(admin.TabularInline):
    model = ChapterAddress
    fieldsets = [
        (None,     {'fields': ['name', 'address1', 'address2', 'city', 'state', 'zip']})
    ]
    extra = 1

class CharacterInline(admin.TabularInline):
    model = Character
    fieldsets = [
        (None,     {'fields': ['name', 'type','dateactive','dateexpiry']})
    ]

class ChapterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'type', 'description']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['name', 'type', 'description']
    inlines = [ChapterAddressInline, StaffInline, CharacterInline]

class AttendanceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['event', 'user', 'character', 'xpawarded', 'authorizedby']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['event', 'user', 'character', 'xpawarded', 'authorizedby', 'rejectedby']

class AttendanceInline(admin.TabularInline):
    model = Attendance
    fieldsets = [
        (None,     {'fields': ['event', 'user', 'character', 'xpawarded', 'authorizedby', 'rejectedby']}),
    ]
    extra = 10

class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['chapter', 'chapteraddress', 'dateheld']}),
    ]
    list_display = ['chapter', 'dateheld']
    inlines = [AttendanceInline]

class AuthorizationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['issuer', 'charactertrait', 'reason', 'authorizinguser', 'authorized', 'dateauthorized']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['issuer', 'charactertrait', 'authorizinguser', 'authorized', 'dateauthorized']

class NoteOwnerInline(admin.TabularInline):
    model = NoteOwner
    fieldsets = [
        (None,     {'fields': ['user', 'character', 'chapter', 'trait', 'traitlevel', 'stafftype']})
    ]
    extra = 3

class NoteTagInline(admin.TabularInline):
    model = NoteTag
    fieldsets = [
        (None,     {'fields': ['tag']})
    ]
    extra = 1

class NoteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['author', 'subject', 'body']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['author', 'subject', 'body']
    inlines = [NoteOwnerInline, NoteTagInline]

class TransactionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['user', 'txnid', 'amount', 'isconsumed']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['user', 'txnid', 'amount', 'isconsumed']

class SubscriptionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['user','name','pp_period3','pp_auth','pp_charset','pp_receiver_email','pp_amount3','pp_form_charset','pp_item_number','pp_payer_email','pp_recurring','pp_last_name','pp_payer_id','pp_mc_amount3','pp_subscr_id','pp_mc_currency','pp_txn_id','pp_txn_type','pp_btn_id','pp_item_name','pp_payer_status','pp_password','pp_reattempt','pp_residence_country','pp_business','pp_subscr_date','pp_first_name','notes']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['user', 'name', 'notes']

class VocabularyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['name', 'displayname', 'displayplural']}),
        ('Active', {'fields': ['dateactive', 'dateexpiry',], 'classes': ['collapse',]})
    ]
    list_display = ['name', 'displayname', 'displayplural']

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CharacterType, CharacterTypeAdmin)
admin.site.register(TraitType, TraitTypeAdmin)
admin.site.register(Trait, TraitAdmin)
admin.site.register(CharacterTrait, CharacterTraitAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(ChapterType, ChapterTypeAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(StaffType, StaffTypeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Vocabulary, VocabularyAdmin)
admin.site.register(Attendance, AttendanceAdmin)

