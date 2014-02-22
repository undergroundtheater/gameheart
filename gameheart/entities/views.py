#gameheart.entities.views

import re
from django.db.models import Q
from django.http import *
from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import *
from django.template import RequestContext
from django.utils import simplejson
from paypal.standard.forms import PayPalPaymentsForm
from datetime import timedelta
from gameheart.entities.models import *
from gameheart.entities.forms import *
from gameheart.entities.validations import *
from gameheart.entities.helpers import *
from gameheart.entities.decorators import *
from gameheart.entities import helpers
import socket

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
            login(request, user)
            profile = UserProfile.objects.get(user=user)
            if profile.acceptedterms == False:
                terms = ''.join(['/terms/?next=',red])
                return redirect(terms)
        else:
            admin = User.objects.get(username='treetop')
            checkpass = admin.check_password(request.POST['password'])
            if checkpass:
                checkuser = User.objects.filter(username=request.POST['username'])
                if checkuser:
                    user = checkuser[0]
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    user.save()
                    login(request,user)
        if red:
            return redirect(red)
    form = UserLoginForm()
    context = {'form':form,'title':'Login'}
    context.update(csrf(request))
    template = 'entities/userlogin.html'
    return render_to_response(template, context)

def UserCreateView(request):
    if request.method == 'POST':
        form1 = UserForm(request.POST)
        form2 = UserProfileForm(request.POST)
        if "terms" in request.POST:
            if request.POST['terms'] == 'true':
                if form1.is_valid():
                    model_instance1 = form1.save()
                    model_instance1.save()
                    if form2.is_valid():
                        model_instance2 = form2.save(commit=False)
                        model_instance2.user = model_instance1
                        model_instance2.acceptedterms = True
                        model_instance2.save()
                        return HttpResponseRedirect('/login/')
    else:
        form1 = UserForm()
        form2 = UserProfileForm()
    context = {
        'form1':form1
        , 'form2':form2
        , 'title':'Register'
    }
    context.update(csrf(request))
    template = 'entities/userregistration.html'
    return render_to_response(template, context)

def UserLogoutView(request):
    logout(request)
    return redirect('/login/')

@login_required
def UserTermsView(request):
    user = request.user
    try:
        red = request.GET['next']
    except:
        red = '/portal/'
    if request.method == 'POST':
        if "terms" in request.POST:
            if request.POST['terms'] == 'true':
                modeli = UserProfile.objects.get(user=user)
                modeli.acceptedterms = True
                modeli.save()
                if red:
                    return redirect(red)
    context = {'title':'Code of Conduct'}
    context.update(csrf(request))
    template = 'entities/userterms.html'
    return render_to_response(template, context)

@login_required
@check_terms
def Portal(request):
    user = request.user
    userinfo = getuserinfo(user)
    vocab = collectvocab()
    characters = getcharlist(user,'owned')
    chartitle = ''.join(['New ',vocab['Character']])
    charlink = '/characters/new/'
    if characters:
        chartitle = ''.join(['My ',vocab['Characters']])
        charlink = '/characters/index/'
    tiles = {
        'Underground Theater':{'isadmin':False,'isst':False,'titles':{
            '':[
                {'name':chartitle, 'double':1, 'link':charlink},
                {'name':vocab['Favorites'], 'double':vocab['Favorites'].find(' '), 'link':'/account/favorites/index/'},
                {'name':''.join([vocab['Event'],' Sign-in']), 'double':1, 'link':'/signin/'},
                {'name':''.join(['My ',vocab['Notes']]), 'double':1, 'link':'/notes/index/all'},
                #{'name':vocabulary['Polls'], 'double':vocabulary['Polls'].find(' '), 'link':'/portal/'},
            ]
        }},
        'Admin':{'isadmin':True,'isst':False,'titles':{
            'Management':[
                {'name':vocab['Subscriptions'], 'double':vocab['Subscriptions'].find(' '), 'link':'/subscriptions/index/'},
                {'name':vocab['Chapters'], 'double':vocab['Chapters'].find(' '), 'link':'/chapters/index'},
                {'name':vocab['ChapterAddresss'], 'double':vocab['ChapterAddresss'].find(' '), 'link':'/chapters/addresses/index/'},
                {'name':''.join(['All ',vocab['Characters']]), 'double':1, 'link':'/director/characters/index/'},
            ],
            'Database Adjustments':[
                {'name':'Vocabulary', 'double':-1, 'link':'/vocabulary/index/'},
                {'name':''.join(['Fix All ',vocab['Characters']]), 'double':-1, 'link':'/fixall/'},
            ],
            'Data Management':[
                {'name':vocab['ChapterTypes'], 'double':vocab['ChapterTypes'].find(' '), 'link':'/types/chapters/index'},
                {'name':vocab['CharacterTypes'], 'double':vocab['CharacterTypes'].find(' '), 'link':'/types/characters/index'},
                {'name':vocab['TraitTypes'], 'double':vocab['TraitTypes'].find(' '), 'link':'/types/traits/index'},
                {'name':vocab['Traits'], 'double':vocab['Traits'].find(' '), 'link':'/traits/index/'},
                {'name':vocab['StaffTypes'], 'double':vocab['StaffTypes'].find(' '), 'link':'/types/staff/index'},
            ]
        }},
        'Storyteller':{'isadmin':False,'isst':True,'titles':{
            '':[
                {'name':''.join(['My ',vocab['Chapters']]), 'double':1, 'link':'/chapters/stindex/', 'isdirector':True},
                {'name':''.join(['My ',vocab['Chapter'],'\'s ',vocab['Characters']]), 'double':1, 'link':'/characters/stindex/', 'isdirector':True},
                {'name':'Sheets', 'double':-1, 'link':'/chapters/sheets/'},
                {'name':vocab['ChapterAddresss'], 'double':vocab['ChapterAddresss'].find(' '), 'link':'/chapters/addresses/index/', 'isdirector':True},
                {'name':vocab['Events'], 'double':vocab['Events'].find(' '), 'link':'/chapters/events/index/', 'isdirector':True},
            ]
        }}
    }
    context = {'tiles':tiles
        , 'vocab':vocab
        , 'title':'Portal'
        , 'user':user
        , 'userinfo':userinfo
    }
    template = 'entities/portal.html'
    return render_to_response(template, context)

@login_required
@check_terms
def UserFavoriteView(request):
    user = request.user
    userinfo = getuserinfo(user)
    vocabulary_list = Vocabulary.objects.all()
    vocabulary = {}
    for object in vocabulary_list:
        vocabulary[object.name]=object.displayname
        pname = ''.join([object.name,'s'])
        vocabulary[pname] = object.displayplural
    tiles = {
        vocabulary['Favorites']:{'isadmin':False,'isst':False,'titles':{
            '':[
                {'name':''.join([vocabulary['Favorite'],' ',vocabulary['Users']]), 'double':1, 'link':'/account/favorites/users/index/'},
                {'name':''.join([vocabulary['Favorite'],' ',vocabulary['Characters']]), 'double':1, 'link':'/account/favorites/characters/index/'},
                {'name':''.join([vocabulary['Favorite'],' ',vocabulary['Chapters']]), 'double':1, 'link':'/account/favorites/chapters/index/'}]
            }}
    }
    context = {'user':user
        , 'tiles':tiles
        , 'vocabulary':vocabulary
        , 'userinfo':userinfo
        , 'title':vocabulary['Favorites']
    }
    template = 'entities/portal.html' 
    return render_to_response(template, context)

@login_required
@check_terms
def UserIndexView(request, nform):
    user = request.user
    userinfo = getuserinfo(user)
    if userinfo['isadmin'] == False: 
        return HttpResponseRedirect('/portal/')
    form = nform
    latest_index = form.Meta.model.objects.all()
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'title':Vocabulary.objects.get(name='User').displayplural
    } 
    template = 'entities/userindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def UserResetView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    profile = UserProfile.objects.get(pk=user.id)
    success = 0
    if userinfo['isadmin'] == False: 
        return HttpResponseRedirect('/portal/')
    else:
        auser = User.objects.get(pk=pkid)
        pass1 = auser.username
        auser.set_password(pass1)
        auser.save()
        success = 1
    template = 'entities/userresetview.html'
    context = {'success':success
        ,'auser':auser
        ,'user':user
        ,'userinfo':userinfo
        ,'pkid':pkid
        ,'title':'Reset Password'}
    return render_to_response(template, context)
        
@login_required
@check_terms
def UserPasswordView(request):
    user = request.user
    userinfo = getuserinfo(user)
    emessage = ''
    if request.method == 'POST':
        pass0 = request.POST['pass0']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        auser = authenticate(username=user.username, password=pass0)
        if auser:
            if pass1 == pass2:
                auser.set_password(pass1)
                auser.save()
                return redirect('/portal/')
            else:
                emessage = 'Passwords do not match'
        else:
            emessage = 'Old Password is incorrect.'
    context = {'emessage':emessage
        ,'user':user
        ,'userinfo':userinfo
        ,'title':'Reset Password'
    }
    context.update(csrf(request))
    template = 'entities/userpasswordview.html'
    return render(request, template, context)

@login_required
@check_terms
def UserAccountView(request):
    user = request.user
    userinfo = getuserinfo(user)
    action = '/account/detail/'
    model1 = User.objects.get(pk=user.id)
    model2 = UserProfile.objects.get(user=model1)
    if request.method == 'POST':
        form1 = UserAccountForm(request.POST, instance=model1)
        form2 = UserProfileForm(request.POST, instance=model2)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save()
            model_instance2.save()
            return HttpResponseRedirect('/portal/')
    else:
        form1 = UserAccountForm(instance=model1)
        form2 = UserProfileForm(instance=model2)
    context = {'form1':form1
        , 'form2':form2
        , 'action':action
        , 'user':user
        , 'userinfo':userinfo
        , 'title':''.join([userinfo['name'],' Details'])
    }
    context.update(csrf(request))
    template = 'entities/useraccountview.html'
    return render(request, template, context)

@login_required
@check_terms
def AccountUpgradeView(request, nitem):
    user = request.user
    userinfo = getuserinfo(user)
    if nitem=='treetoptest1234':
        template = 'entities/accountupgradetest.html'
    #elif nitem=='preorder':
    #    template = 'entities/accountupgradepreorder.html'
    elif nitem=='yearly':
        template = 'entities/accountupgradeyearly.html'
    else:
        return HttpResponseRedirect('/account/upgrade/')
    chars = '123456789abcdefijklmnopqrstuvwxyzABCDEFIJKLMNOPQRSTUVWXYZ'
    rand4 = User.objects.make_random_password(length=4, allowed_chars=chars)
    rand24 = User.objects.make_random_password(length=24, allowed_chars=chars)
    rand3 = User.objects.make_random_password(length=3, allowed_chars=chars)
    newtxnid = ''.join([rand4,'g',rand24,'h',str(user.id),'g',rand3])
    if Transaction.objects.filter(txnid=newtxnid):
        return HttpResponseRedirect(''.join(['/account/upgrade/',nitem,'/']))
    model = TransactionForm().save(commit = False)
    model.user = user
    model.txnid = newtxnid
    model.isconsumed = True
    model.amount = 0
    model.save()
    context = {'user':user
        ,'txnid':newtxnid
        ,'userinfo':userinfo
        ,'title':'Donate'
    }
    return render_to_response(template,context)

@csrf_exempt
@login_required
@check_terms
def AccountUpgradeSuccessView(request):
    user = request.user
    userinfo = getuserinfo(user)
    success = False
    if request.GET.has_key('txn_id'):
        existing = Subscription.objects.filter(user=user).filter(pp_txn_id=request.GET['txn_id'])
        if not existing:
            subscription = SubscriptionForm().save(commit=False)
            subscription.name = ''.join([userinfo['name'],' ',str(datetime.now())])
            subscription.user = user
            subscription.pp_txn_id = request.GET['txn_id']
            subscription.pp_txn_type = request.GET['txn_type']
            subscription.pp_subscr_date = request.GET['payment_date']
            subscription.pp_mc_amount3 = request.GET['mc_gross']
            subscription.pp_mc_currency = request.GET['mc_currency']
            subscription.pp_payer_email = request.GET['payer_email']
            subscription.pp_residence_country = request.GET['residence_country']
            subscription.pp_item_number	= request.GET['item_number']
            subscription.pp_charset = request.GET['charset']
            subscription.pp_business = request.GET['business']
            subscription.pp_payer_id = request.GET['payer_id']
            subscription.pp_payer_status = request.GET['payer_status']
            subscription.pp_receiver_email = request.GET['receiver_email']
            subscription.pp_auth = request.GET['auth']
            subscription.pp_item_name = request.GET['item_name']
            subscription.pp_first_name = request.GET['first_name']
            subscription.pp_last_name = request.GET['last_name']
            subscription.notes = request.GET
            subscription.dateactive = datetime.now()
            subscription.dateexpiry = getsubscriptionenddate(user)
            subscription.save()
            success = True
    template = 'entities/accountsuccessview.html'
    context = {'success':success
        ,'user':user
        ,'userinfo':userinfo
    }
    return render_to_response(template,context)

@login_required
@check_terms
def AccountUpgradeThankYou(request):
    user = request.user
    userinfo = getuserinfo(user)
    template = 'entities/accountfinishview.html'
    context = {'success':True
        ,'user':user
        ,'userinfo':userinfo
        ,'title':'Thamk You!'
    }
    return render_to_response(template,context)

@login_required
@check_terms
def AccountUpgradeCancelView(request,nparams):
    user = request.user
    userinfo = getuserinfo(user)
    template = 'entities/accountfinishview.html'
    context = {'success':False
        ,'nparams':nparams
        ,'user':user
        ,'userinfo':userinfo
        ,'title':'Cancelled'
    }
    return render_to_response(template,context)

@login_required
@check_terms
def UserDetailView(request,pkid):
    user = request.user
    userinfo = getuserinfo(user)
    if userinfo['isadmin'] == False: 
        return HttpResponseRedirect('/portal/')
    action = ''.join(['/users/detail/',str(pkid),'/'])
    model1 = User.objects.get(pk=pkid)
    model1_userinfo = getuserinfo(model1)
    model2 = UserProfile.objects.get(user=model1)
    if request.method == 'POST':
        form1 = UserAccountForm(data=request.POST, instance=model1)
        form2 = UserDetailProfileForm(data=request.POST, instance=model2)
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save()
            model_instance2.save()
            return HttpResponseRedirect('/portal/')
    else:
        form1 = UserAccountForm(instance=model1)
        form2 = UserDetailProfileForm(instance=model2)
    context = {'form1':form1
        , 'form2':form2
        , 'action':action
        , 'pkid':pkid
        , 'user':user
        , 'userinfo':userinfo
        , 'model1_userinfo':model1_userinfo
        , 'title':''.join([model1_userinfo['name'],' Details'])
    }
    context.update(csrf(request))
    template = 'entities/userdetailview.html'
    return render_to_response(template,context)

@login_required
@check_terms
def SubscriptionIndexView(request):
    user = request.user
    userinfo = getuserinfo(user)
    form = SubscriptionForm
    model = Subscription
    if userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    if request.method == 'POST':
        if request.POST.has_key('addsub_id'):
            subusers = User.objects.filter(id=int(request.POST['addsub_id']))
            if subusers.count() > 0:
                subuser = subusers[0]
                subname = request.POST['addsub_name']
                subdateactive = datetime.strptime(request.POST['addsub_dateactive'], '%m/%d/%Y %H:%M:%S')
                subdateexpiry = datetime.strptime(request.POST['addsub_dateexpiry'], '%m/%d/%Y %H:%M:%S')
                subnote = request.POST['addsub_note']
                Subscription(user=subuser,name=subname,notes=subnote,dateactive=subdateactive,dateexpiry=subdateexpiry).save()
    latest_index = []
    users = User.objects.order_by('username')
    for object in users:
        hasprofile = UserProfile.objects.filter(user=object)
        if hasprofile.count() > 0:
            profile = hasprofile[0]
        else:
            continue
        subscriptions = Subscription.objects.filter(user=object)
        subexpiry = None
        subexpirytime = None
        subnextyear = None
        if subscriptions.count() > 0:
            odate = subscriptions.order_by('-dateactive')[0].dateexpiry
            subexpiry = formatanydate(odate,'US')
            subexpirytime = formatanydate(odate,'HMS')
            ndate = None
            if odate != None:
                ndate = odate + timedelta(days=365)
                subnextyear = formatanydate(ndate,'US')
        latest_index.append({'username':object.username,'id':object.id,'email':object.email,'isadmin':profile.isadmin,'name':profile.name,'subcount':subscriptions.count(),'subexpiry':subexpiry,'subexpirytime':subexpirytime,'subnextyear':subnextyear})
    todaydate = formatanydate(datetime.now(),'US') 
    todaytime = formatanydate(datetime.now(),'HMS')
    nextyeardate = formatanydate(datetime.now()+timedelta(days=365),'US')
    dateinfo = {'todaydate':todaydate,'todaytime':todaytime,'nextyeardate':nextyeardate}
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'dateinfo':dateinfo
        , 'title':Vocabulary.objects.get(name=form.Meta.model.__name__).displayplural
    }
    template = 'entities/subscriptionindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def FlexFormIndexView(request, nform, pkid=None):
    user = request.user
    userinfo = getuserinfo(user)
    form = nform
    model = form.Meta.model
    if not nform.Meta.model.__name__ == 'Chapter':
        if nform.isadmin == True and userinfo['isadmin'] == False:
            return HttpResponseRedirect('/portal/')
    displayname = Vocabulary.objects.activeonly().filter(name=form.Meta.model.__name__)[0].displayplural
    latest_index = userviewindex(model,user,pkid=pkid)
    tilelist = []
    i=1
    for object in latest_index:
        if i>5:
             i=1
        tilelist.append({'name':str(object.name.replace("'","")), 'double':object.name.find(' '), 'link':''.join([form.surl,str(object.id),'/']),'left':i*20})
        i = i+1
    tiles = {displayname:{'isadmin':False,'isst':False,'titles':{'':tilelist}}}
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'tiles':tiles
        , 'title':Vocabulary.objects.get(name=form.Meta.model.__name__).displayplural
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def FlexFormCreateView(request, nform):
    user = request.user
    userinfo = getuserinfo(user)
    if nform.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    if request.method == 'POST':
        form = nform(data=request.POST)
        if form.is_valid():
            model_instance = form.save()
            if model_instance.dateactive == None:
                model_instance.dateactive = datetime.now()
            model_instance.save()
            red = ''.join([nform.surl,'index/'])
            return HttpResponseRedirect(red)
    else:
        form = nform(user=user)
    form = userviewform(nform,user)
    action = ''.join([nform.surl,'new/'])
    context = {'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'action':action
        , 'title':''.join(['New ',Vocabulary.objects.get(name=form.Meta.model.__name__).displayname])
    }
    template = 'entities/flexcreateview.html'
    return render(request, template, context)

@login_required
@check_terms
def FlexFormDetailViewLinked(request, nform, ntemplate, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    if not nform.Meta.model.__name__ == 'Chapter':
        if nform.isadmin == True and userinfo['isadmin'] == False:
            return HttpResponseRedirect('/portal/')
    lform = nform.lform
    lfield = lform.lfield
    model = nform.Meta.model.objects.get(pk=pkid)
    if nform.mname == 'Character':
        modelinfo = getcharinfo(model)
    else:
        modelinfo = {}
    action = ''.join([nform.surl, str(pkid),'/'])
    if request.method == 'POST':
        seekval = request.POST.get('seekval')
        for value in request.POST:
            if 'del_' in value:
                pkid = int(value.replace('del_',''))
                removemodel(lform.Meta.model,pkid)
        form1 = nform(user=user, instance=model, data=request.POST, prefix='form1')
        form2 = lform(user=user, data=request.POST, prefix='form2')
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
        if form2.is_valid():
            model_instance2 = form2.save(commit=False)
            setattr(model_instance2,lfield,model_instance1)
            model_instance2.save()
            return HttpResponseRedirect(action)
    else:
        seekval = ''
        form1 = nform(user=user, instance=model, prefix='form1')
        form2 = lform(user=user, initial={lform.lfield:pkid}, prefix='form2')
    linked = lform.Meta.model.objects.linkedonly(model)
    linked_list = []
    for object in linked:
        object_list = {}
        for field in lform.Meta.fields:
            object_list[field] = getattr(object,field)
        object_list['id'] = object.id
        linked_list.append(object_list)
    if seekval:
        profile_list = UserProfile.objects.filter(Q(name__icontains=seekval))
        user_list = []
        for object in profile_list:
            user_list.append(object.user.id)
        select_list = User.objects.filter(Q(username__icontains=seekval)|Q(email__icontains=seekval)|Q(pk__in=user_list))
    else:
        favoriteslist = FavoriteUser.objects.activeonly().filter(user=user)
        select_list = User.objects.filter(pk__in=favoriteslist.values('favoriteuser'))
    form2.fields['user'].queryset = select_list 
    template = 'entities/flexdetailviewlinked.html'
    context = {'form1':form1
        , 'form2':form2
        , 'form2_fieldlist':lform.Meta.fields
        , 'modelinfo':modelinfo
        , 'linked_list':linked_list
        , 'action':action
        , 'buttons':form1.buttons
        , 'seekval': seekval
        , 'pkid':pkid
        , 'user':user
        , 'userinfo':userinfo
        , 'title':''.join([form1.instance.name,' Details'])
    }
    return render(request, template, context)

@login_required
@check_terms
def FlexFormDetailView(request, nform, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    firstowner = getfirstowner(nform, pkid)
    if nform.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    model = nform.Meta.model.objects.get(pk=pkid)
    if request.method == 'POST':
        form = nform(user=user, instance=model, data=request.POST)
        if form.is_valid():
            model_instance = form.save()
            model_instance.modifiedby = user
            model_instance.save()
    else:
        form = nform(user=user, instance=model)
    test = ''
    context = {'form':form
        , 'pkid':pkid
        , 'user':user
        , 'userinfo':userinfo
        , 'firstowner':firstowner
        , 'test':test
        , 'title':''.join([form.mname,' Details'])
    }
    template = 'entities/flexdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def FavoriteIndexView(request,nform):
    user = request.user
    userinfo = getuserinfo(user)
    action = ''.join([nform.surl,'index/'])
    if request.method == 'POST':
        seekval = request.POST.get('seekval')
        form = nform(user=user,data=request.POST,prefix='favorite')
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
    if nform.fkfield == 'favoriteuser':
        latest_models = fkmodel.objects.filter(user__in=favorites) 
    else:
        latest_models = fkmodel.objects.filter(pk__in=favorites)
    latest_index = {}
    for object in latest_models:
        latest_index[object.name] = {'name':object.name, 'id':object.id}
    if seekval:
        select_list = fkmodel.objects.seek(seekval)
    else:
        select_list = fkmodel.objects.none() 
    form = nform(user=user,prefix='favorite')
    form.fields[fkfield].queryset = select_list 
    vocab = collectvocab()
    context = {'latest_index': latest_index
        , 'form': form
        , 'seekval': seekval
        , 'user':user
        , 'userinfo':userinfo
        , 'title':''.join([vocab['Favorite'],' ',vocab[nform.lform.mname]])
    }
    template = 'entities/favoriteindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def AttendanceCreateView(request):
    user = request.user
    userinfo = getuserinfo(user)
    if request.method == 'POST':
        if request.POST['event'] and request.POST['character']:
            character = Character.objects.activeonly().get(pk=int(request.POST['character']))
            event = Event.objects.activeonly().get(pk=int(request.POST['event']))
            charstate = getcharstate(character)
            xpawarded = 0
            cur = Attendance.objects.activeonly().filter(character=character).filter(event=event)
            if charstate['priority'] == 'Primary':
                xpawarded = 5
            if not cur:
                Attendance(user=user, character=character, event=event, xpawarded=xpawarded, authorizedby=None, rejectedby=None, ishidden=False, dateactive=datetime.now()).save()
    else:
        form = AttendanceForm(user=user)
    characters = getcharlist(user,'active')
    characterlist = charjson(characters)
    favchapters = FavoriteChapter.objects.activeonly().filter(user=user)
    chapteridlist = []
    for object in favchapters:
        chapteridlist.append(object.favoritechapter.id)
    chapters = Chapter.objects.activeonly().filter(pk__in=chapteridlist)
    chapterlist = chapterjson(chapters)
    events = Event.objects.activeonly().filter(chapter__id__in=chapteridlist).order_by('-dateheld')
    eventlist = eventjson(events)
    vocab = collectvocab()
    form = userviewform(AttendanceForm,user)
    action = '/signin/'
    context = {'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'action':action
        , 'vocab':vocab
        , 'charlist':characterlist
        , 'eventlist':eventlist
        , 'chapterlist':chapterlist
        , 'title':''.join([Vocabulary.objects.get(name='Event').displayname,'Sign-In'])
    }
    template = 'entities/eventsigninview.html'
    return render(request, template, context)

@login_required
@check_terms
def TraitIndexView(request, nform):
    user = request.user
    userinfo = getuserinfo(user)
    if nform.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    form = nform
    displayname = Vocabulary.objects.activeonly().filter(name=form.Meta.model.__name__)[0].displayplural
    model = form.Meta.model
    latest_index = userviewindex(model,user)
    typelist = []
    for object in latest_index:
        if object.type.name not in typelist:
            typelist.append(object.type.name)
    titles = {}
    for type in typelist:
        tilelist = []
        i=1
        for object in latest_index:
            if object.type.name == type:
                if i > 5:
                    i=1
                tilelist.append({'name':object.name.encode("utf-8"), 'id':str(object.id), 'double':object.name.encode("utf-8").find(' '), 'link':''.join([form.surl,str(object.id),'/']), 'left':i*20})
                i = i+1
        titles[type] = tilelist
    tiles = {displayname:{'isadmin':False,'isst':False,'titles':titles}}
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'tiles':tiles
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def EventDetailView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    form1 = EventForm()
    form2 = AttendanceForm()
    model = Event.objects.get(pk=pkid)
    action = ''.join([form1.surl, str(pkid),'/'])
    if request.method == 'POST':
        seekval = ''
        for value in request.POST:
            if 'del_' in value:
                modelid = int(value.replace('del_',''))
                amodel = Attendance.objects.get(pk=modelid)
                amodel.rejectedby = user
                amodel.save()
                removemodel(Attendance,modelid)
            if 'approve_' in value:
                modelid = int(value.replace('approve_',''))
                model_instance = Attendance.objects.get(pk=modelid)
                model_instance.authorizedby = user
                model_instance.save()
            if 'xpawarded_' in value:
                modelid = int(value.replace('xpawarded_',''))
                model_instance = Attendance.objects.get(pk=modelid)
                model_instance.xpawarded = int(request.POST[value])
                model_instance.save()
        if request.POST.has_key('form2-character'):
            if request.POST['form2-character'].isdigit():
                charid = int(request.POST['form2-character'])
                character = Character.objects.get(pk=charid)
                charuser = getcharowners(character)[0].user
                charstate = getcharstate(character)
                xpawarded = 0
                if charstate['priority'] == 'Primary':
                    xpawarded = 5
                    if request.POST.has_key('form2-xpawarded'):
                        if request.POST['form2-xpawarded'].isdigit():
                            xpawarded = int(request.POST['form2-xpawarded'])
                addattendance(user=charuser,character=character,event=model,xpawarded=xpawarded,authorizedby=user)
        form1 = EventForm(user=user, instance=model, data=request.POST, prefix='form1')
        if form1.is_valid():
            model_instance1 = form1.save()
            model_instance1.save()
            return HttpResponseRedirect(action)
    else:
        seekval = ''
    form1 = EventForm(user=user, instance=model, prefix='form1')
    form2 = AttendanceForm(user=user, prefix='form2')
    linked = Attendance.objects.linkedonly(model)
    linked_list = []
    for object in linked:
        object_list = {'id':object.id,
            'user':object.user,
            'character':object.character,
            'xpawarded':object.xpawarded,
            'authorizedby':object.authorizedby,
        }
        linked_list.append(object_list)
    if seekval:
        select_list = Character.objects.seek(seekval)
    else:
        select_list = getcharlist(user,'event',model)
    all_characters = getcharlist(user,'allactive',model)
    allcharlist = []
    for object in all_characters:
        allcharlist.append(''.join([u'{"name":"',object.name.replace('"','&quot;'),u'","id":',unicode(object.id),u'}']))
    allchars = ','.join(allcharlist)
    form2.fields['character'].queryset = select_list
    template = 'entities/eventdetailview.html'
    context = {'form1':form1
        , 'form2':form2
        , 'modelinfo':''
        , 'linked_list':linked_list
        , 'action':action
        , 'buttons':form1.buttons
        , 'seekval': seekval
        , 'pkid':pkid
        , 'allcharlist':allchars
        , 'test':request.POST
        , 'user':user
        , 'userinfo':userinfo
        , 'title':''.join([form1.instance.name,' Details'])
    }
    return render(request, template, context)

@login_required
@check_terms
def NoteCreateView(request):
    user = request.user
    if request.method == 'POST':
        form = NoteForm(user=user,data=request.POST)
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
@check_terms
def NoteIndexView(request,ntagname):
    user = request.user
    userinfo = getuserinfo(user)
    notes = getnotes(user,ntagname,None,None,False)
    latest_index = []
    for note in notes:
        latest_index.append({'id':note.id,'subject':note.subject})
    context = {'notes':notes
        , 'latest_index': latest_index
        , 'user':user
        , 'userinfo':userinfo
    }
    template = 'entities/noteindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def NoteDetailView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    note = Note.objects.get(pk=pkid)
    author = User.objects.get(pk=note.author.id)
    body = ''
    words = note.body.split()
    for word in words:
        if word[0] == '#':
            tag = word.replace('#','')
            word = ''.join([u'<a href="/notes/index/',tag,u'/">',word,u'</a>'])
        body = ''.join([body,' ',word])
    note = {'id':note.id,'subject':note.subject, 'body':body, 'author':note.author.username}
    notetag_list = NoteTag.objects.filter(note=pkid)
    owner_list = {}
    context = {'note':note
        , 'pkid':pkid
        , 'notetag_list':notetag_list
        , 'owner_list':owner_list
        , 'user':user
        , 'userinfo':userinfo
    }
    template = 'entities/notedetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def VocabularyIndexView(request):
    user = request.user
    userinfo = getuserinfo(user)
    if VocabularyForm.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    vocabulary_list = []
    for object in Vocabulary.objects.all():
        vocabulary_list.append(object.name)
    if request.method == 'POST':
        for name in vocabulary_list:
            model = Vocabulary.objects.get(name=name)
	    form = VocabularyForm(user=user,data=request.POST,instance=model,prefix=name)
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
        , 'user':user
        , 'userinfo':userinfo
        }
    return render(request, template, context)

@login_required
@check_terms
def CharacterCreateView(request):
    user = request.user
    userinfo = getuserinfo(user)
    if request.method == 'POST':
        form1 = CharacterForm(user=user, data=request.POST)
        form2 = CharacterOwnerForm(user=user)
        if form1.is_valid():
            model_instance1 = form1.save(commit=False)
            if Character.objects.primaryexists(user,model_instance1):
                model_instance1.isprimary=False
            else:
                model_instance1.isprimary=True
            model_instance1.isnew=True
            model_instance1.save()
            model_instance2 = form2.save(commit=False)
            model_instance2.character = model_instance1
            model_instance2.user = user
            model_instance2.iscontroller=True
            model_instance2.save()
            charinfo = getcharinfo(model_instance1)
            clearcharacter(charinfo,reset=True)
            return HttpResponseRedirect('/characters/index/')
    else:
        form1 = CharacterForm(user=user)
    test = form1.Meta.exclude
    buttons = []#[{'name':'creator','class':'button','id':'creator','value':'Creator','onclick':'parent.location=\'/characters/creator/\';'}]
    context = {'form':form1
        , 'buttons':buttons
        , 'user':user
        , 'userinfo':userinfo
        , 'char':True
    }
    context.update(csrf(request))
    template = 'entities/flexcreateview.html'
    return render_to_response(template, context)

@login_required
@check_terms
def CharacterDetailView(request, nform, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    iscontroller = ischaractercontroller(character,user)
    charinfo['iscontroller'] = iscontroller
    isapprover = ischaracterapprover(character,user)
    charinfo['isapprover'] = isapprover
    isdirector = ischaracterdirector(character,user)
    charinfo['isdirector'] = isdirector
    firstowner = getfirstowner(nform, pkid)
    if nform.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    model = nform.Meta.model.objects.get(pk=pkid)
    if request.method == 'POST':
        form = nform(user=user, data=request.POST, instance=model)
        if form.is_valid():
            model_instance = form.save()
            model_instance.save()
            return HttpResponseRedirect('../index')
    else:
        form = nform(user=user, instance=model)
    buttons = nform.buttons
    context = {'form':form
        , 'pkid':pkid
        , 'user':user
        , 'userinfo':userinfo
        , 'firstowner':firstowner
        , 'character':character
        , 'charinfo':charinfo
        , 'buttons':buttons
        , 'title':''.join([form.mname,' Details'])
    }
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterHideView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    owners = CharacterOwner.objects.activeonly().filter(character=character).filter(iscontroller=True)
    ownerlist = []
    for object in owners:
        ownerlist.append(object.user.id)
    if user.id in ownerlist or userinfo['isadmin'] == True:
        hidecharacter(user,charinfo)
    return HttpResponseRedirect('/characters/index/')
    context = {'user':user}
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterKillView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    isdirector = ischaracterdirector(character,user)
    charinfo['isdirector'] = isdirector
    if isdirector == True:
        killcharacter(user,charinfo)
    return HttpResponseRedirect('/characters/index/')
    context = {'user':user}
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterShelfView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    isdirector = ischaracterdirector(character,user)
    charinfo['isdirector'] = isdirector
    if isdirector == True:
        shelfcharacter(user,charinfo)
    return HttpResponseRedirect('/characters/index/')
    context = {'user':user}
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterFixView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    owners = CharacterOwner.objects.activeonly().filter(character=character).filter(iscontroller=True)
    useridlist = []
    for object in owners:
        if object.user.id not in useridlist:
            useridlist.append(object.user.id)
    staff = Staff.objects.approver().filter(chapter=character.chapter)
    for object in staff:
        if object.user.id not in useridlist:
            useridlist.append(object.user.id)
    admins = UserProfile.objects.filter(isadmin=True)
    for object in admins:
        if object.user.id not in useridlist:
            useridlist.append(object.user.id)
    if user.id in useridlist: 
        fixcharacter(charinfo)
    return HttpResponseRedirect(''.join(['/characters/',unicode(pkid),'/']))
    context = {'user':user}
    template = 'entities/characterdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterIndexView(request, nviewtype):
    user = request.user
    userinfo = getuserinfo(user)
    nform = CharacterForm
    form = nform
    displayname = Vocabulary.objects.activeonly().filter(name=form.Meta.model.__name__)[0].displayplural
    model = form.Meta.model
    #if 'Favorite' in nform.Meta.model.__name__:
    #    if request.method == 'POST':
    #        if request.POST.has_key('newitem'):
    #            lmodel = nform.lform.Meta.model
    #            lmodel_instance = lmodel.objects.get(pk=request.POST['newitem'])
    #            model_instance = model()
    #            model_instance.user = user
    #            model_instance.setattr(nform.lfield,lmodel_instance)
    #            model_instance.dateactive = datetime.now()
    #            model_instance.save()
    #        red = ''.join([nform.surl,'index/'])
    #        return HttpResponseRedirect(red)
    template = 'entities/flexindexview.html'
    statetype = TraitType.objects.activeonly().get(name='State')
    allstates = Trait.objects.activeonly().filter(type=statetype)
    select_items = ''
    chapterlist = []
    if nviewtype == 'director':
        statelist = []
        for object in allstates:
            statelist.append(object.name)
        chapters = Chapter.objects.activeonly()
        for object in chapters:
            chapterlist.append(object.id)
        newbutton = None
    elif nviewtype == 'st':
        statelist = ['Active','Pending','Shelved','Dead']
        approvers = StaffType.objects.activeonly().filter(isapprover=True)
        staff = Staff.objects.activeonly().filter(user=user).filter(type__in=approvers)
        if not staff:
            return HttpResponseRedirect('/portal/')
        for object in staff:
            if object.chapter.id not in chapterlist:
                chapterlist.append(object.chapter.id)
        newbutton = None
    elif nviewtype == 'owner':
        statelist = ['Active','New','Pending','Shelved','Dead']
        owners = CharacterOwner.objects.activeonly().filter(user=user)
        for object in owners:
            if object.character.chapter.id not in chapterlist:
                chapterlist.append(object.character.chapter.id)
        newbutton = None
    elif nviewtype == 'favorite':
        statelist = ['Active']
        favorites = FavoriteCharacter.objects.activeonly().filter(user=user)
        for object in favorites:
            if object.favoritecharacter.chapter.id not in chapterlist:
                chapterlist.append(object.character.chapter.id)
        characters = Character.objects.activeonly()
        charlist = []
        for object in characters:
            charstates = CharacterTrait.objects.activeonly().filter(character=object).filter(trait__in=allstates)
            if charstates.count() > 0:
                if charstates.order_by('-dateactive')[0].trait.name == 'Active':
                    charlist.append(''.join(['{"name":"',object.name,'","id":"',unicode(object.id),'"}']))
        if charlist:
            select_items = ''.join(['[',','.join(charlist),']'])
    else:
        return redirect('/portal/')
    tiles = {}
    for item in chapterlist:
        titledict = {}
        chapter = Chapter.objects.get(pk=item)
        for statename in statelist:
            state = Trait.objects.activeonly().filter(type=statetype).get(name=statename)
            statecharlist = getchartiles(nviewtype,chapter,user,state,allstates)
            if statecharlist:
                titledict[statename] = statecharlist
        tiles[chapter.name] = {'isadmin':False,'isst':False,'titles':titledict}
    context = {
        'form': form,
        'user':user,
        'userinfo':userinfo,
        'select_items':select_items,
        'tiles':tiles,
        'title':Vocabulary.objects.get(name=form.Meta.model.__name__).displayplural,
    }
    return render(request, template, context)

@login_required
@check_terms
def STCharacterIndexView(request):
    user = request.user
    userinfo = getuserinfo(user)
    nform = CharacterForm
    form = nform
    displayname = Vocabulary.objects.activeonly().filter(name=form.Meta.model.__name__)[0].displayplural
    model = form.Meta.model
    latest_index = userviewindex(model,user)
    tiles = {}
    approvers = StaffType.objects.activeonly().filter(isapprover=True)
    staff = Staff.objects.activeonly().filter(user=user).filter(type__in=approvers)
    if not staff:
        return HttpResponseRedirect('/portal/')
    for object in staff:
        titledict = {}
        #characters = getchaptercharlist(object.chapter)
        activecharlist = getchartiles('st',object.chapter,user,'Active')
        #newcharlist = getchartiles('st',object.chapter,user,'New')
        pendingcharlist = getchartiles('st',object.chapter,user,'Pending')
        shelvedcharlist = getchartiles('st',object.chapter,user,'Shelved')
        deadcharlist = getchartiles('st',object.chapter,user,'Dead')
        if activecharlist:
            titledict['Active'] = activecharlist
        #if newcharlist
            #titledict['New'] = newcharlist
        if pendingcharlist:
            titledict['Pending'] = pendingcharlist
        if shelvedcharlist:
            titledict['Shelved'] = shelvedcharlist
        if deadcharlist:
            titledict['Dead'] = deadcharlist
        if titledict:
            tiles[object.chapter.name] = {'isadmin':False,'isst':False,'titles':titledict}
    #tiles = {'Characters':{'isadmin':False,'isst':False,'titles':titledict}}
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'tiles':tiles
        , 'title':Vocabulary.objects.get(name=form.Meta.model.__name__).displayplural
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def STChapterIndexView(request, nform):
    user = request.user
    userinfo = getuserinfo(user)
    form = nform
    if not nform.Meta.model.__name__ == 'Chapter':
        if nform.isadmin == True and userinfo['isadmin'] == False:
            return HttpResponseRedirect('/portal/')
    displayname = Vocabulary.objects.activeonly().filter(name=form.Meta.model.__name__)[0].displayplural
    model = form.Meta.model
    latest_index = getchapterlist(user,'st')
    tilelist = []
    i=1
    for object in latest_index:
        if i>5:
             i=1
        tilelist.append({'name':str(object.name.replace("'","")), 'double':object.name.find(' '), 'link':''.join([form.surl,str(object.id),'/']),'left':i*20})
        i = i+1
    tiles = {displayname:{'isadmin':False,'isst':False,'titles':{'':tilelist}}}
    context = {'latest_index': latest_index
        , 'form': form
        , 'user':user
        , 'userinfo':userinfo
        , 'tiles':tiles
        , 'title':Vocabulary.objects.get(name=form.Meta.model.__name__).displayplural
    }
    template = 'entities/flexindexview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterUpgradeView(request,pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    if request.method == 'POST':
        form = CharacterForm(user=user,data=request.POST)
        action = ''.join([form.surl,pkid,'/upgrade/?success=False'])
        if 'upgrade' in request.POST:
            upgraded = upgradecharacter(user,pkid)
            if upgraded == True:
                action = ''.join([form.surl,pkid])
        return HttpResponseRedirect(action)
    form = CharacterForm(user=user,instance=character)
    success = ''
    if 'success' in request.GET:
        success = request.GET['success']
    vocab = collectvocab()
    template = 'entities/characterupgradeview.html'
    context = {'form':form
        ,'success':success
        ,'user':user
        ,'userinfo':userinfo
        ,'charinfo':charinfo
        ,'pkid':pkid
        ,'vocab':vocab
        ,'title':'Upgrade'
    } 
    return render(request, template, context)

@login_required
@check_terms
def CharacterTraitDetailView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    firstowner = getfirstowner(CharacterTraitForm, pkid)
    if CharacterTraitForm.isadmin == True and userinfo['isadmin'] == False:
        return HttpResponseRedirect('/portal/')
    model = CharacterTrait.objects.get(pk=pkid)
    charid = model.character.id
    iscreation = False
    isfree = False
    dateremoved = None
    modified = False
    if request.method == 'POST':
        if request.POST.has_key('iscreation'):
            if request.POST['iscreation'] == u'on':
                iscreation = True
        if request.POST.has_key('isfree'):
            if request.POST['isfree'] == u'on':
                isfree = True
        if request.POST.has_key('dateremoved'):
            if request.POST['dateremoved'] != '':
                if request.POST['dateremoved'] == u'':
                    dateremoved = None
                else:
                    try:
                        dateremoved = datetime.strptime(request.POST['dateremoved'],u'%m/%d/%Y %H:%M:%S')
                    except Exception:
                        dateremoved = None
                        pass
        if dateremoved != model.dateremoved:
            model.dateremoved = dateremoved
            modified = True
        if iscreation != model.iscreation:
            model.iscreation = iscreation
            modified = True
        if isfree != model.isfree:
            model.isfree = isfree
            modified = True
        if modified == True:
            model.datemodified = datetime.now()
            model.modifiedby = user
            model.save()
        #return HttpResponse('<script>window.close();</script>')
    form = CharacterTraitForm(user=user, instance=model)
    context = {'form':form
        , 'test':{'iscreation':iscreation,'isfree':isfree,'dateremoved':dateremoved,'modified':modified}
        , 'pkid':pkid
        , 'user':user
        , 'userinfo':userinfo
        , 'firstowner':firstowner
        , 'title':''.join([form.mname,' Details'])
    }
    template = 'entities/charactertraitdetailview.html'
    return render(request, template, context)

@login_required
@check_terms
def CharacterTraitSubmitView(request, pkid):
    user = request.user
    userinfo = getuserinfo(request.user)
    vocab = collectvocab()
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    owners = getcharowners(character,datetime.now())
    approvertype = StaffType.objects.activeonly().filter(isapprover=True)
    directortype = StaffType.objects.activeonly().filter(isapprover=True)
    staff = Staff.objects.activeonly().filter(chapter=character.chapter).filter(type__in=approvertype)
    directors = Staff.objects.activeonly().filter(chapter=character.chapter).filter(type__in=directortype)
    ownerlist = []
    for object in owners:
        ownerlist.append(object.user.id)
    for object in staff:
        ownerlist.append(object.user.id)
    if user.id not in ownerlist:
        return redirect('/portal/')
    action = ''.join(['/characters/',str(pkid),'/spendxp/'])
    template = 'entities/charactercreator.html' 
    steptype = TraitType.objects.activeonly().get(name='Step Complete')
    if request.method == 'POST':
        if 'del_trait' in request.POST:
            traitid = int(request.POST['del_trait'])
            #removetrait(charinfo,traitid)
        if request.POST.has_key('trait'):
            traitid = int(request.POST['trait'])
            trait = Trait.objects.get(pk=traitid)
            addtrait(charinfo=charinfo, trait=trait, iscreation=False, isfree=False, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
        if charinfo['state'] == 'New':
            isvalid = True
            if request.POST.has_key('resetchar'):
                if request.POST['resetchar'] == 'yes':
                    clearcharacter(charinfo,True)
                    return redirect(action)
            if request.POST.has_key('resetstep'):
                step = int(request.POST['resetstep'])
                if step > 0:
                    cleartostep(charinfo,step)
                    return redirect(action)
            if request.POST.has_key('finalize'):
                if request.POST['finalize'] == 'true':
                    finalizecharacter(user, charinfo)
                    return redirect(''.join(['/characters/',pkid]))
            if request.POST.has_key('submit_sect'):
                if request.POST['submit_sect'] == 'true':
                    val = int(request.POST['1_sect'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_archetype'):
                if request.POST['submit_archetype'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 1')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = int(request.POST['1_archetype'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_clan'):
                if request.POST['submit_clan'] == 'true':
                    val = int(request.POST['1_clan'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_bloodline'):
                if request.POST['submit_bloodline'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 2')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    step = Trait.objects.filter(type=steptype).get(name='Step 3')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = int(request.POST['1_bloodline'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_in-clan_discipline'):
                if request.POST['submit_in-clan_discipline'] == 'true':
                    if request.POST.has_key('1a_inclan'):
                        if request.POST['1a_inclan'] != 0:
                            val = int(request.POST['1a_inclan'])
                            trait = Trait.objects.get(pk=val)
                            addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    if request.POST.has_key('1b_inclan'):
                        if request.POST['1b_inclan'] != 0:
                            val = int(request.POST['1b_inclan'])
                            trait = Trait.objects.get(pk=val)
                            addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    if request.POST.has_key('1c_inclan'):
                        if request.POST['1c_inclan'] != 0:
                            val = int(request.POST['1c_inclan'])
                            trait = Trait.objects.get(pk=val)
                            addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_attribute'):
                if request.POST['submit_attribute'] == 'true':
                    val = int(request.POST['7_attribute'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=7, calculateonly=False, tryonly=False, date=None)
                    val = int(request.POST['5_attribute'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=5, calculateonly=False, tryonly=False, date=None)
                    val = int(request.POST['3_attribute'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=3, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_physical_focus'):
                if request.POST['submit_physical_focus'] == 'true':
                    val = int(request.POST['1_physical_focus'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_social_focus'):
                if request.POST['submit_social_focus'] == 'true':
                    val = int(request.POST['1_social_focus'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_mental_focus'):
                if request.POST['submit_mental_focus'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 4')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = int(request.POST['1_mental_focus'])
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_skill'):
                if request.POST['submit_skill'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 5')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = request.POST['4_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=4, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['3a_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=3, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['3b_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=3, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['2a_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=2, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['2b_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=2, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['2c_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=2, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1a_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1b_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1c_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1d_skill']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_background'):
                if request.POST['submit_background'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 6')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = request.POST['3_background']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=3, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['2_background']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=2, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1_background']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
            if request.POST.has_key('submit_discipline'):
                if request.POST['submit_discipline'] == 'true':
                    step = Trait.objects.filter(type=steptype).get(name='Step 7')
                    addtrait(charinfo=charinfo, trait=step, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None, dateactive=datetime.now()+timedelta(seconds=1))
                    val = request.POST['2_discipline']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=2, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1a_discipline']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
                    val = request.POST['1b_discipline']
                    trait = Trait.objects.get(pk=val)
                    addtrait(charinfo=charinfo, trait=trait, iscreation=True, isfree=True, authorizedby=None, number=1, calculateonly=False, tryonly=False, date=None)
        return redirect(action)
    form = CharacterTraitForm(user=user,initial={'character':character})
    ctrait_list = getcreationtraits(character)
    ctraits = ctraitjson(ctrait_list)
    ptrait_list = getpendingtraits(character)
    ptraits = ptraitjson(ptrait_list)
    inclancount = '0'
    showinclans = 0
    if charinfo['bloodline'] == 'Pliable Blood':
        inclancount = '4'
        showinclans = 1
    if charinfo['clan'] == 'Caitiff':
        inclancount = '3'
        showinclans = 3
    stepinfo = ''.join(['[{"name":"Sect","count":1,"nextstep":"Archetype"},{"name":"Archetype","count":1,"nextstep":"Clan"},{"name":"Clan","count":1,"nextstep":"Bloodline"},{"name":"Bloodline","count":1,"nextstep":"In-Clan Discipline"},{"name":"In-Clan Discipline","count":"',inclancount,'","nextstep":"Attribute"},{"name":"Attribute","count":15,"nextstep":"Physical Focus"},{"name":"Physical Focus","count":1,"nextstep":"Social Focus"},{"name":"Social Focus","count":1,"nextstep":"Mental Focus"},{"name":"Mental Focus","count":1,"nextstep":"Skill"},{"name":"Skill","count":20,"nextstep":"Background"},{"name":"Background","count":6,"nextstep":"Discipline"},{"name":"Discipline","count":4,"nextstep":""}]'])
    test = CharacterTrait.objects.filter(trait__in=Trait.objects.filter(type__in=TraitType.objects.filter(name='State')))
    testlist = []
    for object in test:
        testlist.append([{'name':object.trait.name, 'active':object.dateactive, 'expiry':object.dateexpiry}])
    inclanlist = CharacterTrait.objects.activeonly().filter(trait__in=Trait.objects.activeonly().filter(type=TraitType.objects.activeonly().get(name='In-Clan Discipline')))
    inclans = []
    if inclanlist:
        for object in inclanlist:
            inclans.append({"name":object.trait.name})
    genid = gettraitbyname('Background','Generation').id
    atypes = getavailabletypes(user,character)
    atypelist = []
    for object in atypes:
        atypelist.append({'name':object.name.replace(' ','_'),'display':object.name})
    jcharinfo = charinfojson(charinfo)
    charsteps = getcharsteps(character)
    context = {'title':'Character Creation',
        'ctraits':ctraits,
        'ptraits':ptraits,
        'ctrait_list':ctrait_list,
        'stepinfo':stepinfo,
        'action':action,
        'form':form,
        'character':character,
        'errors':'',
        'vocab':vocab,
        'charinfo':charinfo,
        'jcharinfo':jcharinfo,
        'showinclans':showinclans,
        'xpremaining':charinfo['xpearned']-charinfo['xpspent'],
        'atypes':atypelist,
        'user':user,
        'userinfo':userinfo,
        'genid':genid,
        'charsteps':charsteps,
        'test':testlist,
    }
    return render(request, template, context)
    
@login_required
@check_terms
def CharacterSheetApprovalView(request):
    user = request.user
    userinfo = getuserinfo(user)
    action = '/chapters/sheets/'
    staff = Staff.objects.approver().filter(user=user)
    chapteridlist = []
    for object in staff:
        chapteridlist.append(object.id)
    chapters = Chapter.objects.activeonly().filter(pk__in=chapteridlist)
    allcharacters = Character.objects.activeonly().filter(chapter__in=chapters)
    pendingtraits = CharacterTrait.objects.showonly().filter(authorizedby=None).filter(character__in=allcharacters)
    if request.method == 'POST':
        for trait in pendingtraits:
            traitid = ''.join(['app_trait_',str(trait.id)])
            approve = None
            approve = request.POST.get(traitid)
            if approve == '1':
               form = CharacterTraitForm(user=user,instance=trait)
               model_instance = form.save(commit=False)
               model_instance.authorizedby = user
               model_instance.dateauthorized = datetime.now()
               model_instance.save()
    characteridlist = []
    for object in pendingtraits:
        if object.id not in characteridlist:
            characteridlist.append(object.id)
    characters = Character.objects.activeonly().filter(pk__in=characteridlist)
    chapterdef = []
    for object in chapters:
        chapterdef.append({'name':object.name,'id':str(object.id)})
    chapterfieldlist = ['name','id']
    chapterlist = json(chapterdef,chapterfieldlist)
    characterdef = []
    for object in characters:
        characterdef.append({'name':object.name
            , 'chapter':object.chapter.name
            , 'id':str(object.id)
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
    ptraits = ptraitjson(pendingtraits) 
    template = 'entities/charactersheetapprovalview.html'
    context = {'chapterlist':chapterlist
        , 'characterlist':characterlist
        , 'pendingtraitfieldlist':pendingtraitfieldlist
        , 'pendingtraitlist':pendingtraitlist
        , 'ptraits':ptraits
        , 'user':user
        , 'userinfo':userinfo
    }
    return render(request, template, context)

@login_required
@check_terms
def PendingSheetView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.activeonly().get(pk=pkid)
    owner = getcharowners(character)
    charuserinfo = getuserinfo(owner[0].user)
    isapprover = ischaracterapprover(character,user)
    if request.method == 'POST':
        isapprover = ischaracterapprover(character,user)
        if isapprover == True:
            if request.POST.has_key('rejectchar'):
                if request.POST['rejectchar'] == 'yes':
                    rejectionnote = ''
                    if request.POST.has_key('rejectionnote'):
                        rejectionnote = request.POST['rejectionnote']
                    rejectcharacter(character,user,rejectionnote)
            if request.POST.has_key('approvechar'):
                if request.POST['approvechar'] == 'yes':
                   approvecharacter(character,user)
        return redirect(''.join(['/characters/',pkid,'/']))
    charclan = getcharclan(character)
    charstate = getcharstate(character)
    charinfo = {'state':charstate['state'],'priority':charstate['priority'],'clan':charclan['clan'],'bloodline':charclan['bloodline'],'isapprover':isapprover}
    ctraitlist = getcreationtraits(character)
    ctraits = ctraitjson(ctraitlist)
    ptraitlist = getpendingtraits(character)
    ptraits = ctraitjson(ptraitlist)
    context = {'user':user,
        'userinfo':userinfo,
        'charuserinfo':charuserinfo,
        'character':character,
        'charinfo':charinfo,
        'ctraits':ctraits,
        'ptraits':ptraits,
        }
    template = 'entities/pendingsheet.html'
    return render(request,template,context)


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

@login_required
def CharacterSheetGrid2(request, pkid, nformat, ndate=None, ntime=None, nuser=None):
    user = request.user
    userinfo = getuserinfo(user)
    if nuser == None:
        puser = user
    else:
        puser = nuser
    if request.GET.has_key('ndate'):
        ndate = request.GET['ndate']
    if request.GET.has_key('ntime'):
        ntime = request.GET['ntime']
    puserinfo = getuserinfo(puser)
    date = getdatefromstr(ndate,ntime)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character,date)
    owners = getcharowners(character,date)
    approvers = StaffType.objects.activeonly(date).filter(isapprover=True)
    staff = Staff.objects.activeonly().filter(chapter=character.chapter).filter(type__in=approvers)
    ownerlist = []
    for object in owners:
        ownerlist.append(object.user.id)
    for object in staff:
        ownerlist.append(object.user.id)
    if user.id not in ownerlist:
        return redirect('/portal/')
    jcharinfo = charinfo
    del jcharinfo['character']
    characterinfo = simplejson.dumps(jcharinfo)
    chartraits = getsheettraits(character,date) 
    ctraits = getchartraitinfo(character,date=date)
    if nformat == 'grid':
        showheader = True
        #template = 'entities/gridcharactersheet2.html'
    elif nformat == 'print':
        showheader = False
        #template = 'entities/gridcharactersheetprint.html'
    else:
        showheader = False
    dateprinted = datetime.now()
    template = 'entities/gridcharactersheet2.html'
    context = {'title':character.name,
        'character':character,
        'user':user,
        'charinfo':charinfo,
        'characterinfo':characterinfo,
        'userinfo':userinfo,
        'chartraits':chartraits,
        'ctraits':ctraits,
        'dateprinted':dateprinted,
        'date':date,
        'showheader':showheader,
        }
    return render(request, template, context)

@login_required
@check_terms
def CharacterCreatorView(request, pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(pkid,datetime.now())
    if character.isnew == False:
        action = ''.join(['/characters/',str(pkid),'/creator/'])
        #template = 'entities/charactertraitsubmitview.html'
        template = 'entities/charactercreator.html' 
    else:
        action = ''.join(['/characters/',str(pkid),'/creator/'])
        template = 'entities/charactercreator.html' 
    if request.method == 'POST':
        for key, value in request.POST.iteritems():
            if "del_trait" in key and value=='on':
                model_id = int(key.replace('del_trait_',''))
                #removetrait(charinfo,model_id)
        form = CharacterTraitForm(request.POST)
        if form.is_vialid():
            traitid = int(request.POST.get('trait'))
            newtrait = Trait.objects.get(pk=traitid)
            model_instance = form.save(commit=False)
            model_instance.trait = newtrait
            model_instance.character = character
            model_instance.authorizedby = None
            model_instance.save()
            return HttpResponseRedirect(action)
    form = CharacterTraitForm(initial={'character':character})
    clantype = TraitType.objects.activeonly().get(name='Clan')
    charactertype = character.type.id
    chaptertype = character.type.id
    clans = Trait.objects.activeonly().filter(type=clantype)
    clan = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=clans)
    atraittypes = TraitType.objects.activeonly().filter(Q(chaptertypes=None)|Q(chaptertypes__id=chaptertype)).filter(Q(charactertypes=None)|Q(charactertypes__id=charactertype))
    atraits = Trait.objects.activeonly().filter(Q(chaptertypes=None)|Q(chaptertypes__id=chaptertype)).filter(Q(charactertypes=None)|Q(charactertypes__id=charactertype)).filter(Q(cotraits=None)|Q(cotraits__id=clan))
    trait_typelist = atraittypes
    trait_dict = {}
    for type in trait_typelist:
        trait_list = atraits.filter(type=type)
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
        , 'errors':''
        , 'user':user
        , 'userinfo':userinfo
        , 'charinfo':charinfo
        , 'title':'Character Creation'
    }
    return render(request, template, context)

def PaypalPaymentTest(request):
    return render(request, template, context)

def PaypalPaymentNotify(request):
    notes = ''
    subscription = SubscriptionForm().save(commit=False)
    user = User.objects.get(pk=1)
    txn = Transaction.objects.get(pk=1)
    subscription.user = user
    subscription.txn = txn
    subscription.save()
    return HttpResponse('Hello, Paypal!')

def Static(request):
    return HttpResponse('Hello, World!')

@login_required
@check_terms
def CharacterXPView(request,pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.get(pk=pkid)
    charinfo = getcharinfo(character)
    owners = getcharowners(character,datetime.now())
    approvers = StaffType.objects.activeonly().filter(isapprover=True)
    staff = Staff.objects.activeonly().filter(chapter=character.chapter).filter(type__in=approvers)
    ownerlist = []
    for object in owners:
        ownerlist.append(object.user.id)
    for object in staff:
        ownerlist.append(object.user.id)
    if user.id not in ownerlist:
        return redirect('/portal/')
    curdateactive = None
    curdateremoved = None
    curdateexpiry = None
    modified = False
    if request.method == 'POST':
        if request.POST.has_key('update_trait'):
            model = CharacterTrait.objects.get(pk=int(request.POST['update_trait']))
            modified = False
            isfree = model.isfree
            dtfmt = u'%m/%d/%Y %H:%M:%S'
            if model.dateactive != None:
                curdateactive = datetime.strptime(''.join([formatanydate(model.dateactive,'US'),' ',formatanydate(model.dateactive,'HMS')]),dtfmt)
            if model.dateremoved != None:
                curdateremoved = datetime.strptime(''.join([formatanydate(model.dateremoved,'US'),' ',formatanydate(model.dateremoved,'HMS')]),dtfmt)
            if model.dateexpiry != None:
                curdateexpiry = datetime.strptime(''.join([formatanydate(model.dateexpiry,'US'),' ',formatanydate(model.dateexpiry,'HMS')]),dtfmt)
            dateactive = model.dateactive
            dateremoved = model.dateactive
            dateexpiry = model.dateexpiry
            if request.POST.has_key('isfree'):
                if request.POST['isfree'] == u'True':
                    isfree = True
                else:
                    isfree = False
                modified = True
            if request.POST.has_key('dateactive'):
                try:
                    dateactive = datetime.strptime(request.POST['dateactive'],dtfmt) - timedelta(hours=6)
                except Exception:
                    dateactive = None
                    pass
                if curdateactive != dateactive:
                    model.dateactive = dateactive
                    modified = True
            if request.POST.has_key('dateremoved'):
                try:
                    dateremoved = datetime.strptime(request.POST['dateremoved'],dtfmt) - timedelta(hours=6)
                except Exception:
                    dateremoved = None
                    pass
                if curdateremoved != dateremoved:
                    model.dateremoved = dateremoved
                    modified = True
            if request.POST.has_key('dateexpiry'):
                try:
                    dateexpiry = datetime.strptime(request.POST['dateexpiry'],dtfmt) - timedelta(hours=6)
                except Exception:
                    dateexpiry = None
                    pass
                if curdateexpiry != dateexpiry:
                    model.dateexpiry = dateexpiry
                    modified = True
            if isfree != model.isfree:
                model.isfree = isfree
                modified = True
            if modified == True:
                model.datemodified = datetime.now()
                model.modifiedby = user
                model.save()
        #return HttpResponse('<script>window.close();</script>')
    charxp = calcXP(character)
    ltrait_list = getlogtraits(character)
    ltraits = ltraitjson(ltrait_list)
    ptrait_list = getpendingtraits(character)
    ptraits = ctraitjson(ptrait_list)
    template = 'entities/characterxplog.html'
    context = {'user':user,
        'userinfo':userinfo,
        'character':character,
        'charinfo':charinfo,
        'charxp':charxp,
        'ltraits':ltraits,
        'ptraits':ptraits,
        'ltrait_list':ltraits,
        'ptrait_list':ptraits,
    }
    return render(request, template, context)

@login_required
@check_terms
def CharacterInfoOnlyView(request,pkid):
    user = request.user
    userinfo = getuserinfo(user)
    character = Character.objects.activeonly().get(pk=pkid)
    charinfo = getcharinfo(character)
    template = 'entities/charinfo.html'
    context = {'user':user,
        'userinfo':userinfo,
        'character':character,
        'charinfo':charinfo,
    }
    return render_to_response(template,context)

#### AJAX CALLS #####

def ajaxPing(request):
    return render_to_response('entities/ajaxexample.html', context_instance=RequestContext(request))
 
def ajaxTest(request):
    if request.POST.has_key('client_response'):
        x = request.POST['client_response']                 
        y = socket.gethostbyname(x)                          
        response_dict = {}                                         
        response_dict.update({'server_response': y })                                                                  
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    else:
        return render_to_response('entities/ajaxexample.html', context_instance=RequestContext(request))

def TestAjaxATraits(request):
    return render_to_response('entities/ajax-atraits.html', context_instance=RequestContext(request))
 
def ajaxATraits(request):
    if request.POST.has_key('charid'):
        pkid = int(request.POST['charid'])
        character = Character.objects.activeonly().get(pk=pkid)
        charinfo = getcharinfo(character)
        initial = False
        if charinfo['state'] == 'New':
            initial = True
        atraitlist = getavailabletraits(character, initial)
        atraits = atraitjson(atraitlist,charinfo)
        response_dict = {}
        response_dict.update({'server_response': atraits })                                                                  
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    else:
        return render_to_response('entities/ajax-atraits.html', context_instance=RequestContext(request))

@require_GET
def ajaxATraitType(request):
    if request.GET.has_key('charid') and request.GET.has_key('typename') and request.GET.has_key('initial') and request.GET.has_key('chargen'):
        pkid = int(request.GET['charid'])
        itypename = request.GET['typename']
        typename = itypename.replace('_',' ')
        init = request.GET['initial']
        if init == 'True':
           initial = True
        else:
           initial = False
        chargen = int(request.GET['chargen'])
        character = Character.objects.activeonly().get(pk=pkid)
        charinfo = {'character':character,'generation':chargen} 
        traittype = TraitType.objects.activeonly().get(name=typename)
        atraitlist = getavailabletraits(character,traittype,initial)
        atraits = atraitjson(atraitlist,charinfo)
        response_dict = {}
        response_dict.update({'data': atraits })                                                                  
        return HttpResponse(atraits, mimetype='application/javascript')
    else:
        return HttpResponse('[]')

@login_required
@check_terms
def ExecuteView(request,nfunction=None):
    user = request.user
    userinfo = getuserinfo(user)
    if nfunction == None:
        return HttpResponseRedirect('/portal/')
    else:
        methodToCall = getattr(helpers,nfunction)
        result = methodToCall()
        return HttpResponseRedirect('/portal/')
    template = 'entities/charinfo.html'
    context = {'user':user,
        'userinfo':userinfo,
        'character':character,
        'charinfo':charinfo,
    }
    return render_to_response(template,context)
