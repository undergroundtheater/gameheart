#gameheart.entities.views

from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from gameheart.entities.models import *
from gameheart.entities.forms import *
from gameheart.entities.validations import *
from gameheart.entities.helpers import *

def test(request):
    return HttpResponse('Hello World!')

def UserLoginView(request):
    try:
        red = request.GET['next']
        if request.user.is_authenticated():
            return redirect(red)
    except:
        red = '/portal/'
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            if user.is_active:
                login(request, user)
        if red:
            return redirect(red)
    form = UserLoginForm()
    context = {'form':form}
    context.update(csrf(request))
    template = 'entities/userlogin.html'
    return render_to_response(template, context)

def UserCreateView(request):
    if request.method == 'POST':
        form1 = UserForm(request.POST)
        form2 = UserProfileForm(request.POST)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save(commit=False)
            model_instance2.user = model_instance1
            model_instance2.save()
            return HttpResponseRedirect('../index')
    else:
        form1 = UserForm()
        form2 = UserProfileForm()
    context = {
        'form1':form1
        , 'form2':form2
    }
    context.update(csrf(request))
    template = 'entities/userregistration.html'
    return render_to_response(template, context)

@login_required
def UserUpgradeView(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    # What you want the button to do.
    siteurl = 'http://127.0.0.1:8080'
    notify_url = ''.join([siteurl,'/gameheart/receiver/patrons/upgrade/upgradenow/'])
    return_url = ''.join([siteurl,'/thankyou/'])
    cancel_url = ''.join([siteurl,'/cancel/'])
    paypal_dict = {
        'business': 'jjneylon@gmail.com',
        'amount': '0.01',
        'item_name': 'Underground Theatre Yearly Subscription',
        'invoice': '001',
        'notify_url': notify_url,
        'return_url': return_url, 
        'cancel_return': cancel_url 
        }
    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    return render_to_response('entities/payment.html', context)

def UserLogoutView(request):
    logout(request)
    return redirect('/login/')

@login_required
def Portal(request, ptemplate):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    userinfo = getuserinfo(user)
    vocabulary_list = Vocabulary.objects.all()
    vocabulary = {}
    for object in vocabulary_list:
        vocabulary[object.name]=object.displayname
        pname = ''.join([object.name,'s'])
        vocabulary[pname] = object.displayplural
    tiles = {
        'Underground Theatre':{'isadmin':False,'isst':False,'titles':{
            '':[
                [''.join(['My ',vocabulary['Characters']]), '/characters/index'],
                [''.join(['New ',vocabulary['Character']]), '/characters/new/'],
                [''.join([vocabulary['Favorite'],' ',vocabulary['Users']]), '/favorites/users/'],
                [''.join([vocabulary['Favorite'],' ',vocabulary['Characters']]), '/favorites/characters/'],
                [''.join([vocabulary['Favorite'],' ',vocabulary['Chapters']]), '/favorites/chapters/']]
            }},
        'Admin':{'isadmin':True,'isst':False,'titles':{
            'Management':[
                [vocabulary['Users'], '/users/index'],
                [vocabulary['Chapters'], '/chapters/index'],
                [vocabulary['ChapterAddresss'], '/chapters/addresses/index/'],
                [vocabulary['Traits'], '/traits/index/'],
                ['Vocabulary', '/vocabulary/index/']],
            
            'Types':[
                [vocabulary['ChapterTypes'], '/types/chapters/index'],
                [vocabulary['CharacterTypes'], '/types/characters/index'],
                [vocabulary['TraitTypes'], '/types/traits/index'],
                [vocabulary['StaffTypes'], '/types/staff/index']]
            }},
        'Storyteller':{'isadmin':False,'isst':True,'titles':{
            '':[
                {'name':vocabulary['Chapters'], 'link':'/chapters/index/'},
                {'Sheets', '/chapters/sheets/'}]
            }}
    }
    context = {'user':user
        , 'profile':profile
        , 'tiles':tiles
        , 'vocabulary':vocabulary
        , 'userinfo':userinfo
    }
    template = ptemplate
    return render_to_response(template, context)

@login_required
def UserIndexView(request, nform):
    user = request.user
    form = nform
    latest_index = form.Meta.model.objects.all()
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
    } 
    template = 'entities/userindexview.html'
    return render(request, template, context)

@login_required
def UserDetailView(request, pkid):
    user = request.user
    model1 = User.objects.get(pk=pkid)
    model2 = UserProfile.objects.get(user=model1)
    if request.method == 'POST':
        form1 = UserForm(request.POST, instance=model1)
        form2 = UserProfileForm(request.POST, instance=model2)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save()
            model_instance2.save()
            return HttpResponseRedirect('../index')
    else:
        form1 = UserForm(instance=model1)
        form2 = UserProfileForm(instance=model2)
    context = {'form1':form1
        , 'form2':form2
        , 'pkid':pkid
        , 'user':user
    }
    context.update(csrf(request))
    template = 'entities/userdetailview.html'
    return render_to_response(template, context)

@login_required
def FlexFormIndexView(request, nform):
    user = request.user
    form = nform
    latest_index = form.Meta.model.objects.activeonly()
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
def FlexFormCreateView(request, nform):
    user = request.user
    if request.method == 'POST':
        form = nform(request.POST)
        if form.is_valid():
            model_instance = form.save()
            model_instance.save()
            return HttpResponseRedirect('../index')
    else:
        form = nform
    context = {'form': form, 'user':user}
    template = 'entities/flexcreateview.html'
    return render(request, template, context)

@login_required
def FlexFormDetailViewLinked(request, nform, ntemplate, pkid):
    user = request.user
    lform = nform.lform
    lfield = lform.lfield
    model = nform.Meta.model.objects.get(pk=pkid)
    action = ''.join([nform.surl, str(pkid)])
    if request.method == 'POST':
        form1 = nform(request.POST, instance=model)
        form2 = lform(request.POST)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save(commit=False)
            setattr(model_instance2,lfield,model_instance1)
            model_instance2.save()
            return HttpResponseRedirect(action)
        else:
            return HttpResponseRedirect(action)
    else:
        form1 = nform(instance=model)
        form2 = lform(initial={lform.lfield:pkid})
    linked = lform.Meta.model.objects.linkedonly(model)
    linked_list = []
    for object in linked:
        object_list = {}
        for field in lform.Meta.fields:
            object_list[field] = getattr(object,field)
        linked_list.append(object_list)
    context = {'form1':form1
        , 'form2':form2
        , 'form2_fieldlist':lform.Meta.fields
        , 'linked_list':linked_list
        , 'action':action
        , 'pkid':pkid
        , 'user':user
    }
    template = ''.join(['entities/',ntemplate])
    return render(request, template, context)

@login_required
def FlexFormDetailView(request, nform, pkid):
    user = request.user
    model = nform.Meta.model.objects.get(pk=pkid)
    if request.method == 'POST':
        form = nform(request.POST, instance=model)
        if form.is_valid():
            model_instance = form.save()
            model_instance.save()
            return HttpResponseRedirect('../index')
    else:
        form = nform(instance=model)
    context = {'form':form, 'pkid':pkid, 'user':user}
    template = 'entities/flexdetailview.html'
    return render(request, template, context)

@login_required
def ChapterDetailView(request, pkid):
    user = request.user
    model = Chapter.objects.get(pk=pkid)
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=model)
        if form.is_valid():
            model_instance = form.save()
            model_instance.save()
            return HttpResponseRedirect('../index')
    else:
        form = nform(instance=model)
    context = {'form':form, 'pkid':pkid, 'user':user}
    template = 'entities/flexdetailview.html'
    return render(request, template, context)

@login_required
def ChapterIndexView(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    form = ChapterForm
    staffof = Staff.objects.activeonly().filter(user=user)
    if profile.isadmin == True:
        latest_index = Chapter.objects.activeonly()
    elif staffof:
        latest_index = Chapter.objects.activeonly().filter(pk__in=staffof.chapter)
    else:
        latest_index = Chapter.objects.none()
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
def FavoriteIndexView01(request):
    user = request.user
    action = '/favorites/characters/'
    if request.method == 'POST':
        seekval = request.POST.get('seekval')
        form = FavoriteCharacterForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)
            curlist = form.Meta.model.objects.filter(pk=model_instance.id)
            if curlist:
                return HttpResponseRedirect(action)
            model_instance.user = user
            model_instance.save()
            return HttpResponseRedirect(action)
    else:
        seekval = ''
    favorites = FavoriteCharacter.objects.filter(user=user) 
    latest_index = Character.objects.filter(pk__in=favorites)
    if seekval:
        select_list = Character.objects.seek(seekval)
    else:
        select_list = Character.objects.none() 
    form = FavoriteCharacterForm()
    form.fields['favoritecharacter'].queryset = select_list 
    context = {'latest_index': latest_index
        , 'form': form
        , 'seekval': seekval
        , 'user':user
    }
    template = 'entities/favoriteindexview.html'
    return render(request, template, context)

@login_required
def FavoriteIndexView(request,nform):
    user = request.user
    action = nform.surl
    if request.method == 'POST':
        seekval = request.POST.get('seekval')
        form = nform(request.POST,prefix='favorite')
        if form.is_valid():
            model_instance = form.save(commit=False)
            curlist = form.Meta.model.objects.filter(pk=model_instance.id)
            if curlist:
                return HttpResponseRedirect(action)
            model_instance.user = user
            model_instance.save()
            return HttpResponseRedirect(action)
    else:
        seekval = ''
    fkfield = nform.fkfield
    favorites = nform.Meta.model.objects.filter(user=user).values(fkfield)
    fkmodel = nform.fkmodel
    latest_models = fkmodel.objects.filter(pk__in=favorites)
    latest_index = {}
    if nform.fkfield == 'favoriteuser':
        for object in latest_models:
            latest_index[object.username] = {'name':object.username, 'id':object.id}
        if seekval:
            select_list = fkmodel.objects.filter(username__contains=seekval)
        else:
            select_list = fkmodel.objects.none() 
    else:
        for object in latest_models:
            latest_index[object.name] = {'name':object.name, 'id':object.id}
        if seekval:
            select_list = fkmodel.objects.seek(seekval)
        else:
            select_list = fkmodel.objects.none() 
    form = nform(prefix='favorite')
    form.fields[fkfield].queryset = select_list 
    context = {'latest_index': latest_index
        , 'form': form
        , 'seekval': seekval
        , 'user':user
    }
    template = 'entities/favoriteindexview.html'
    return render(request, template, context)

@login_required
def NoteCreateView(request):
    user = request.user
    if request.method == 'POST':
        form = NoteForm(request.POST)
        tform = NoteTagForm()
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.author=user
            model_instance.save()
            words=model_instance.body.split()
            for word in words:
                if word[0]=='#':
                    model_instance2 = tform.save(commit=False)
                    model_instance2.note = model_instance
                    model_instance2.tag = word.replace('#', '')
                    model_instance2.save()
            action = ''.join(['/notes/',str(model_instance.id),'/'])
            return HttpResponseRedirect(action)
    else:
        form = NoteForm
    context = {'form': form
        , 'user': user
    }
    template = 'entities/flexcreateview.html'
    return render(request, template, context)

@login_required
def NoteIndexView(request,ntagname):
    user = request.user
    tag = ntagname
    form = NoteForm
    model = userfilter(Note, user)
    if ntagname != 'all':
        notetag_list = NoteTag.objects.filter(tag=tag)
    else:
        notetag_list = NoteTag.objects.all()
    notes = model.filter(id__in=notetag_list.values('note'))
    latest_index = {}
    for note in notes:
        words = note.body.split()
        body = ''
        for word in words:
            if word[0] == '#':
                tag = word.replace('#','')
                word = ''.join([u'<a href="/notes/index/',tag,u'/">',word,u'</a>'])
            body = ''.join([body,' ',word])
        latest_index[note.id] = {'subject':note.subject, 'body':body}
    context = {'notes':notes
        , 'latest_index': latest_index
        , 'form': form
        , 'user':user
    }
    template = 'entities/noteindexview.html'
    return render(request, template, context)

@login_required
def NoteDetailView(request, pkid):
    user = request.user
    model = Note.objects.get(pk=pkid)
    author = User.objects.get(pk=model.author.pk)
    body = ''
    words = model.body.split()
    for word in words:
        if word[0] == '#':
            tag = word.replace('#','')
            word = ''.join([u'<a href="/notes/index/',tag,u'/">',word,u'</a>'])
        body = ''.join([body,' ',word])
    note = {'subject':model.subject, 'body':body, 'author':author.username}
    notetag_list = NoteTag.objects.filter(note=pkid)
    owner_list = {}
    context = {'note':note
        , 'pkid':pkid
        , 'notetag_list':notetag_list
        , 'owner_list':owner_list
        , 'user':user
    }
    template = 'entities/notedetailview.html'
    return render(request, template, context)

@login_required
def VocabularyIndexView(request):
    user = request.user
    vocabulary_list = []
    for object in Vocabulary.objects.all():
        vocabulary_list.append(object.name)
    if request.method == 'POST':
        for name in vocabulary_list:
            model = Vocabulary.objects.get(name=name)
	    form = VocabularyForm(request.POST,instance=model,prefix=name)
            if form.is_valid():
                model_instance = form.save()
                model_instance.save()
        red = ''.join(['/vocabulary/index/', ''])
        return HttpResponseRedirect(red)
    form_list = {}
    for name in vocabulary_list:
        model = Vocabulary.objects.get(name=name) 
        form = VocabularyForm(instance=model, prefix=name)
        form_list[name] = form
    template = 'entities/vocabularyindex.html'
    context = {'vocabulary_list':vocabulary_list
        , 'form_list':form_list
        }
    return render(request, template, context)

@login_required
def CharacterCreateView(request):
    user = request.user
    if request.method == 'POST':
        form1 = CharacterForm(request.POST)
        form2 = CharacterOwnerForm()
        if form1.is_valid():
            model_instance1 = form1.save(commit=False)
            if Character.objects.primaryexists(user,model_instance1):
                model_instance1.isprimary=0
            else:
                model_instance1.isprimary=1
            model_instance1.save()
            model_instance2 = form2.save(commit=False)
            model_instance2.character = model_instance1
            model_instance2.user = user
            model_instance2.save()
            return HttpResponseRedirect('/portal/')
    else:
        form1 = CharacterForm()
    context = {
        'form':form1
        , 'user':user
    }
    context.update(csrf(request))
    template = 'entities/flexcreateview.html'
    return render_to_response(template, context)

@login_required
def CharacterDetailView(request, nform, pkid):
    user = request.user
    model1 = Character.objects.get(pk=pkid)
    if request.method == 'POST':
        form1 = CharacterForm(request.POST, instance=model1)
        form2 = CharacterOwnerForm(request.POST)
        s = [form1.surl, str(pkid)]
        red = ''.join(s)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save(commit=False)
            model_instance2.character = model_instance1
            model_instance2.save()
            return HttpResponseRedirect('../index/')
        else:
            return HttpResponseRedirect(red)
    else:
        form1 = CharacterForm(instance=model1)
        form2 = CharacterOwnerForm(initial={'character':pkid})
    owner_list = CharacterOwner.objects.filter(character=model1)
    context = {'form1':form1
        , 'form2':form2
        , 'owner_list':owner_list
        , 'pkid':pkid
        , 'user':user
    }
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
def CharacterIndexView(request):
    user = request.user
    form = CharacterForm
    owner_list = CharacterOwner.objects.filter(user=user)
    latest_index = Character.objects.filter(id__in=owner_list.values('character'))
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
def CharacterTraitSubmitView(request, pkid):
    user = request.user
    character = Character.objects.get(pk=pkid)
    action = ''.join(['/characters/',str(pkid),'/test/'])
    if request.method == 'POST':
        for key, value in request.POST.iteritems():
            if "del_trait" in key and value=='on':
                model_id = int(key.replace('del_trait_',''))
                del_model = CharacterTrait.objects.get(pk=model_id)
                del_model_instance = CharacterTraitForm(instance=del_model).save(commit=False)
                del_model_instance.dateexpiry = datetime.now()
                del_model_instance.save()
        form = CharacterTraitForm(request.POST)
        if form.is_valid():
            traitid = int(request.POST.get('trait'))
            newtrait = Trait.objects.get(pk=traitid)
            model_instance = form.save(commit=False)
            model_instance.trait = newtrait
            model_instance.character = character
            model_instance.authorizedby = None
            model_instance.save()
            return HttpResponseRedirect(action)
    form = CharacterTraitForm(initial={'character':character})
    trait_typelist = TraitType.objects.all()
    trait_dict = {}
    for type in trait_typelist:
        trait_list = Trait.objects.filter(type=type)
        traittypes = {}
        for trait in trait_list:
            traitdetails = {}
            for field in TraitForm.fieldlist:
                traitdetails[field] = getattr(trait,field)
            traittypes[trait.name] = traitdetails
        trait_dict[type.name] = traittypes
    charactertraits = CharacterTrait.objects.activeonly().filter(character=character).filter(authorizedby=None)
    pendingtrait_list = {}
    for charactertrait in charactertraits:
        objectid = charactertrait.id
        trait = Trait.objects.get(pk=charactertrait.trait.id)
        traittypeid = trait.type.id
        traittype = TraitType.objects.get(pk=traittypeid).name
        pendingtrait_list[trait.name] = {'name':trait.name,'type':traittype,'id':trait.id,'objectid':objectid}
    context = {'trait_dict':trait_dict
        , 'pendingtrait_list':pendingtrait_list
        , 'charactertraits':charactertraits
        , 'action':action
        , 'form':form
        , 'character':character
    }
    template = 'entities/charactertraitsubmitview.html' 
    return render(request, template, context)
    
@login_required
def CharacterSheetApprovalView(request):
    user = request.user
    action = '/chapters/sheets/'
    staff = Staff.objects.approver().filter(user=user)
    staffchapters = staff.values('chapter')
    chapters = Chapter.objects.activeonly().filter(pk__in=staffchapters)
    allcharacters = Character.objects.activeonly().filter(chapter__in=chapters)
    pendingtraits = CharacterTrait.objects.activeonly().filter(authorizedby=None).filter(character__in=allcharacters)
    characters = Character.objects.activeonly().filter(pk__in=pendingtraits.values('character'))
    if request.method == 'POST':
        test = request.POST.get('app_trait_1')
        for trait in pendingtraits:
            traitid = ''.join(['app_trait_',str(trait.id)])
            approve = request.POST.get(traitid)
            if approve == '1':
               form = CharacterTraitForm(instance=trait)
               model_instance = form.save(commit=False)
               model_instance.authorizedby = user
               model_instance.save()
               test = ''.join([traitid,' saved by ',user.username])
            approve = None
    else:
        test = '0'
    chapterdef = []
    for object in chapters:
        chapterdef.append({'name':object.name,'id':str(object.id)})
    chapterfieldlist = ['name','id']
    chapterlist = json(chapterdef,chapterfieldlist)
    characterdef = []
    for object in characters:
        characterdef.append({'name':object.name
            ,'chapter':object.chapter.name
            ,'id':str(object.id)
        })
    characterfieldlist = ['name','chapter','id']
    characterlist = json(characterdef,characterfieldlist)
    pendingtraitdef = []
    for object in pendingtraits:
        pendingtraitdef.append({'character':object.character.name
            , 'chapter':object.character.chapter.name
            , 'trait':object.trait.name
            , 'traittype':object.trait.type.name
            , 'id':str(object.id)
        })
    pendingtraitfieldlist = ['character','chapter','trait','traittype','id']
    pendingtraitlist = json(pendingtraitdef,pendingtraitfieldlist)
    template = 'entities/charactersheetapprovalview.html'
    context = {'chapterlist':chapterlist
        , 'characterlist':characterlist
        , 'pendingtraitfieldlist':pendingtraitfieldlist
        , 'pendingtraitlist':pendingtraitlist
        , 'test':test
    }
    return render(request, template, context)

@login_required
def CharacterSheetView01(request, pkid):
    user = request.user
    form = CharacterSheetForm
    cform = CharacterForm
    tform = TraitForm
    ttform = TraitTypeForm    
    character_info = cform.Meta.model.objects.filter(id=pkid).order_by('-datecreated')
    character_traits = form.Meta.model.objects.filter(character=pkid).order_by('-datecreated')
    trait_types_list = ttform.Meta.model.objects.all().order_by('-datecreated')
    traits_list = tform.Meta.model.objects.all().order_by('type')
    clan_list = traits_list.filter(type__in=ttform.Meta.model.objects.filter(name='Clan'))
    context = {'character_info': character_info
        , 'character_traits': character_traits
        , 'pkid': pkid
        , 'traits_list':traits_list
        , 'trait_types_list':trait_types_list
        , 'clan_list':clan_list 
        , 'user':user
        }
    template = 'entities/charactersheet01.html' 
    return render(request, template, context)

@login_required
def CharacterSheetView02(request, pkid):
    user = request.user
    if request.method == 'POST':
        iform1 = CharacterTraitForm(request.POST)
        if iform1.is_valid():
            model_instance = iform1.save()
            model_instance.save()
            return HttpResponseRedirect('../sheet')
    else:
        iform1 = CharacterTraitForm(initial={'character':pkid})
    model = Character.objects.get(pk=pkid)
    form = CharacterForm(instance=model)
    context = {'form':form, 'iform1':iform1, 'pkid':pkid, 'user':user}
    template = 'entities/charactersheet02.html'
    return render(request, template, context)

@login_required
def CharacterSheetView03(request, pkid):
    user = request.user
    clan_type = TraitType.objects.filter(name='Clan')
    temper_type = TraitType.objects.filter(name='Temper')
    attribute_type = TraitType.objects.filter(name='Attribute')
    skill_type = TraitType.objects.filter(name='Skill')
    merit_type = TraitType.objects.filter(name='Merit')
    flaw_type = TraitType.objects.filter(name='Flaw')
    discipline_type = TraitType.objects.filter(name='Discipline')
    if request.method == 'POST':
        iform01 = CharacterTraitForm(request.POST,prefix='clan')
        iform02 = CharacterTraitForm(request.POST,prefix='temper')
        iform03 = CharacterTraitForm(request.POST,prefix='attribute')
        iform04 = CharacterTraitForm(request.POST,prefix='skill')
        iform05 = CharacterTraitForm(request.POST,prefix='merit')
        iform06 = CharacterTraitForm(request.POST,prefix='flaw')
        iform07 = CharacterTraitForm(request.POST,prefix='discipline')
        if iform01.is_valid():
            model_instance01 = iform01.save()
            model_instance01.save()
        if iform02.is_valid():
            model_instance02 = iform02.save()
            model_instance02.save()
        if iform03.is_valid():
            model_instance03 = iform03.save()
            model_instance03.save()
        if iform04.is_valid():
            model_instance04 = iform04.save()
            model_instance04.save()
        if iform05.is_valid():
            model_instance05 = iform05.save()
            model_instance05.save()
        if iform06.is_valid():
            model_instance06 = iform06.save()
            model_instance06.save()
        if iform07.is_valid():
            model_instance07 = iform07.save()
            model_instance07.save()
        return HttpResponseRedirect('/characters/'+str(pkid)+'/sheet/')
    else:
        clan_list = Trait.objects.filter(type__in=clan_type)
        temper_list = Trait.objects.filter(type__in=temper_type)
        attribute_list = Trait.objects.filter(type__in=attribute_type)
        skill_list = Trait.objects.filter(type__in=skill_type)
        merit_list = Trait.objects.filter(type__in=merit_type)
        flaw_list = Trait.objects.filter(type__in=flaw_type)
        discipline_list = Trait.objects.filter(type__in=discipline_type)
        iform01 = CharacterTraitForm(initial={'character':pkid},prefix='clan')
        iform02 = CharacterTraitForm(initial={'character':pkid},prefix='temper')
        iform03 = CharacterTraitForm(initial={'character':pkid},prefix='attribute')
        iform04 = CharacterTraitForm(initial={'character':pkid},prefix='skill')
        iform05 = CharacterTraitForm(initial={'character':pkid},prefix='merit')
        iform06 = CharacterTraitForm(initial={'character':pkid},prefix='flaw')
        iform07 = CharacterTraitForm(initial={'character':pkid},prefix='discipline')
        iform01.fields['trait'].queryset = clan_list 
        iform02.fields['trait'].queryset = temper_list 
        iform03.fields['trait'].queryset = attribute_list 
        iform04.fields['trait'].queryset = skill_list 
        iform05.fields['trait'].queryset = merit_list 
        iform06.fields['trait'].queryset = flaw_list 
        iform07.fields['trait'].queryset = discipline_list 
    trait_type_list = TraitType.objects.all()
    trait_list = Trait.objects.all()
    char_clan_list = CharacterTrait.objects.filter(character=pkid, trait__in=clan_list)
    char_temper_list = CharacterTrait.objects.filter(character=pkid, trait__in=temper_list)
    char_attribute_list = CharacterTrait.objects.filter(character=pkid, trait__in=attribute_list)
    char_skill_list = CharacterTrait.objects.filter(character=pkid, trait__in=skill_list)
    char_merit_list = CharacterTrait.objects.filter(character=pkid, trait__in=merit_list)
    char_flaw_list = CharacterTrait.objects.filter(character=pkid, trait__in=flaw_list)
    char_discipline_list = CharacterTrait.objects.filter(character=pkid, trait__in=discipline_list)
    model = Character.objects.get(pk=pkid)
    form = CharacterForm(instance=model)
    template = 'entities/charactersheet03.html'
    context = {'form':form
        , 'iform01':iform01
        , 'iform02':iform02
        , 'iform03':iform03
        , 'iform04':iform04
        , 'iform05':iform05
        , 'iform06':iform06
        , 'iform07':iform07
        , 'pkid':pkid
        , 'char_clan_list':char_clan_list
        , 'char_temper_list':char_temper_list
        , 'char_attribute_list':char_attribute_list
        , 'char_skill_list':char_skill_list
        , 'char_merit_list':char_merit_list
        , 'char_flaw_list':char_flaw_list
        , 'char_disicpline_list':char_discipline_list
        }
    return render(request, template, context)

@login_required
def CharacterSheetView04(request, pkid):
    user = request.user
    clan_type = TraitType.objects.filter(name='Clan')
    temper_type = TraitType.objects.filter(name='Temper')
    attribute_type = TraitType.objects.filter(name='Attribute')
    skill_type = TraitType.objects.filter(name='Skill')
    merit_type = TraitType.objects.filter(name='Merit')
    flaw_type = TraitType.objects.filter(name='Flaw')
    discipline_type = TraitType.objects.filter(name='Discipline')
    if request.method == 'POST':
        iform01 = CharacterTraitForm(request.POST,prefix='clan')
        iform02 = CharacterTraitForm(request.POST,prefix='temper')
        iform03 = CharacterTraitForm(request.POST,prefix='attribute')
        iform04 = CharacterTraitForm(request.POST,prefix='skill')
        iform05 = CharacterTraitForm(request.POST,prefix='merit')
        iform06 = CharacterTraitForm(request.POST,prefix='flaw')
        iform07 = CharacterTraitForm(request.POST,prefix='discipline')
        if iform01.is_valid():
            model_instance01 = iform01.save()
            model_instance01.save()
        if iform02.is_valid():
            model_instance02 = iform02.save()
            model_instance02.save()
        if iform03.is_valid():
            model_instance03 = iform03.save()
            model_instance03.save()
        if iform04.is_valid():
            model_instance04 = iform04.save()
            model_instance04.save()
        if iform05.is_valid():
            model_instance05 = iform05.save()
            model_instance05.save()
        if iform06.is_valid():
            model_instance06 = iform06.save()
            model_instance06.save()
        if iform07.is_valid():
            model_instance07 = iform07.save()
            model_instance07.save()
        return HttpResponseRedirect('/characters/'+str(pkid)+'/sheet/')
    else:
        clan_list = Trait.objects.filter(type__in=clan_type)
        temper_list = Trait.objects.filter(type__in=temper_type)
        attribute_list = Trait.objects.filter(type__in=attribute_type)
        skill_list = Trait.objects.filter(type__in=skill_type)
        merit_list = Trait.objects.filter(type__in=merit_type)
        flaw_list = Trait.objects.filter(type__in=flaw_type)
        discipline_list = Trait.objects.filter(type__in=discipline_type)
        iform01 = CharacterTraitForm(initial={'character':pkid},prefix='clan')
        iform02 = CharacterTraitForm(initial={'character':pkid},prefix='temper')
        iform03 = CharacterTraitForm(initial={'character':pkid},prefix='attribute')
        iform04 = CharacterTraitForm(initial={'character':pkid},prefix='skill')
        iform05 = CharacterTraitForm(initial={'character':pkid},prefix='merit')
        iform06 = CharacterTraitForm(initial={'character':pkid},prefix='flaw')
        iform07 = CharacterTraitForm(initial={'character':pkid},prefix='discipline')
        iform01.fields['trait'].queryset = clan_list 
        iform02.fields['trait'].queryset = temper_list 
        iform03.fields['trait'].queryset = attribute_list 
        iform04.fields['trait'].queryset = skill_list 
        iform05.fields['trait'].queryset = merit_list 
        iform06.fields['trait'].queryset = flaw_list 
        iform07.fields['trait'].queryset = discipline_list 
    trait_type_list = TraitType.objects.all()
    trait_list = Trait.objects.all()
    char_clan_list = CharacterTrait.objects.filter(character=pkid, trait__in=clan_list)
    char_temper_list = CharacterTrait.objects.filter(character=pkid, trait__in=temper_list)
    char_attribute_list = CharacterTrait.objects.filter(character=pkid, trait__in=attribute_list)
    char_skill_list = CharacterTrait.objects.filter(character=pkid, trait__in=skill_list)
    char_merit_list = CharacterTrait.objects.filter(character=pkid, trait__in=merit_list)
    char_flaw_list = CharacterTrait.objects.filter(character=pkid, trait__in=flaw_list)
    char_discipline_list = CharacterTrait.objects.filter(character=pkid, trait__in=discipline_list)
    model = Character.objects.get(pk=pkid)
    form = CharacterForm(instance=model)
    template = 'entities/charactersheet03.html'
    context = {'form':form
        , 'iform01':iform01
        , 'iform02':iform02
        , 'iform03':iform03
        , 'iform04':iform04
        , 'iform05':iform05
        , 'iform06':iform06
        , 'iform07':iform07
        , 'pkid':pkid
        , 'char_clan_list':char_clan_list
        , 'char_temper_list':char_temper_list
        , 'char_attribute_list':char_attribute_list
        , 'char_skill_list':char_skill_list
        , 'char_merit_list':char_merit_list
        , 'char_flaw_list':char_flaw_list
        , 'char_disicpline_list':char_discipline_list
        }
    return render(request, template, context)

@login_required
def CharacterSheetView05(request, pkid):
    user = request.user
    trait_type_list = []
    action = ''.join(['/characters/', str(pkid), '/sheet/'])
    for object in TraitType.objects.all():
        trait_type_list.append(object.name)
    if request.method == 'POST':
        for name in trait_type_list:
	    iform = CharacterTraitForm(request.POST,prefix=name)
            if iform.is_valid():
                model_instance = iform.save()
                model_instance.save()
        return HttpResponseRedirect(action)
    form_list = {}
    char_trait_list = {}
    for name in trait_type_list:
        type_list = TraitType.objects.filter(name=name)
        trait_list = Trait.objects.filter(type__in=type_list)
        iform = CharacterTraitForm(initial={'character':pkid}, prefix=name)
        iform.fields['trait'].queryset = trait_list
        form_list[name] = iform
        char_list = CharacterTrait.objects.filter(character=pkid, trait__in=trait_list)
        char_trait_list[name] = char_list
    model = Character.objects.get(pk=pkid)
    form = CharacterForm(instance=model)
    template = 'entities/charactersheet05.html'
    context = {'form':form
        , 'trait_type_list':trait_type_list
        , 'form_list':form_list
        , 'char_trait_list':char_trait_list
        , 'action':action
        , 'pkid':pkid
        }
    return render(request, template, context)

@login_required
def CharacterSheetView06(request, pkid):
    user = request.user
    action = ''.join(['/characters/', str(pkid), '/test/'])
    if request.method == 'POST':
        return HttpResponseRedirect(action)
    trait_type_list = TraitType.objects.activeonly()
    trait_list = Trait.objects.activeonly()
    traits = {}
    for typename in trait_type_list:
        traitobjects = trait_list.filter(type=typename)
        traitlist = {}
        for traitname in traitobjects:
            traitlist[traitname.name] = [traitname,traitobjects.level,traitobjects.xpcost]
        traits[typename] = traitlist
    template = 'entities/charactersheet06.html'
    context = {'traits':traits}
    return render(request, template, context)

@login_required
def CharacterSheetGrid(request, pkid, ndate=None, ntime=None, nuser=None):
    user = request.user
    if nuser == None:
        puser = user
    else:
        puser = nuser
    effectivedate = getdate(ndate,ntime) 
    character = Character.objects.activeonly(effectivedate).get(pk=pkid)
    characterowners = CharacterOwner.objects.activeonly().filter(character=character).filter(user=user)
    if not characterowners:
        return HttpResponseRedirect('/portal/')
    onepertraittypes = TraitType.objects.activeonly(effectivedate).filter(onepercharacter=True)
    onepertraits = Trait.objects.activeonly(effectivedate).filter(type__in=onepertraittypes)
    oneperchartraits = CharacterTrait.objects.activeonly(effectivedate).filter(character=character).filter(trait__in=onepertraits)
    characterdict = {'name':character.name,'owner':puser.username}
    characterfieldlist = ['name','owner']
    for object in oneperchartraits:
        characterdict[object.trait.type.name]=str(object.trait.name)
        characterfieldlist.append(object.trait.type.name)
    characterinfo = json([characterdict],characterfieldlist)
    alltraittypes = TraitType.objects.activeonly(effectivedate).filter(onepercharacter=False)
    alltraits = Trait.objects.activeonly(effectivedate).filter(type__in=alltraittypes)
    allactivetraits = CharacterTrait.objects.activeonly(effectivedate).filter(character=character).filter(trait__in=alltraits)
    traitdict = {}
    traitlist = []
    for object in allactivetraits:
        if object.trait.name not in traitdict:
            count=0
            for item in allactivetraits:
                if item.trait.name == object.trait.name:
                    count = count+1
            traitname = object.trait.name
            traitdict[traitname] = {'name':object.trait.name,'type':object.trait.type.name, 'count':str(count),'aggregate':str(object.trait.type.aggregate),'onepercharacter':str(object.trait.type.onepercharacter)}
            traitlist.append(traitdict[traitname])
    traits = json(traitlist,['name','type','count','aggregate','onepercharacter'])
    traittypelist = []
    for object in alltraittypes:
        traittypelist.append({'name':object.name,'id':str(object.id),'aggregate':str(object.aggregate),'onepercharacter':str(object.onepercharacter)})
    traittypes = json(traittypelist,['name','id','aggregate','onepercharacter'])
    action = ''.join(['/character/',str(pkid),'/print/'])
    grid = gridformat(characterdict,traitlist,traittypelist)
    template = 'entities/gridcharactersheet.html'
    context = {'character':character 
        , 'characterinfo':characterinfo
        , 'action':action
        , 'traits':traits
        , 'traittypes':traittypes
        , 'character':character
        , 'pkid':pkid
        , 'puser':puser
        , 'effectivedate':effectivedate
        , 'grid':grid
        }
    return render(request, template, context)














