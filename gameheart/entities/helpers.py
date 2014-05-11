#helpers

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from datetime import datetime, timedelta, date, time
from calendar import monthrange
from django.db.models import Q, Sum
from gameheart.entities.models import *
from gameheart.entities.forms import *
from django.shortcuts import redirect
from django.utils import simplejson
from math import floor

def formatanydate(thisdate,dformat='US'):
    if thisdate == None:
        return '--'
    elif dformat == 'US':
        dateformat = u'%m/%d/%Y'
    elif dformat == 'HMS':
        dateformat = u'%H:%M:%S'
    elif dformat == 'USHMS':
        dateformat = u'%m/%d/%Y %H:%M:%S'
    elif dformat == 'url':
        dateformat = u'?ndate=%Y%m%d&ntime=%H%M'
    elif dformat == 'flatstr':
        dateformat = u'%Y%m%d'
    elif dformat == 'militarytime':
        dateformat = u'%H%M'
    datestr = thisdate.strftime(dateformat)
    return datestr

def sortdict(ndict):
    keys = []
    for k,v in ndict.iteritems():
        keys.append(k)
    sortedkeys = sorted(keys)
    sorteddict = {}
    for key in sortedkeys:
        sorteddict[key] = ndict[key]
    return sorteddict

def j(stringlist,delimiter=''):
    return delimiter.join(stringlist)

def json(dictlist, fieldlist):
    objstrlist = []
    for object in dictlist:
        fieldstrlist = []
        for field in fieldlist:
            fieldstrlist.append(''.join(['"',field,'":"',object[field],'"']))
        objstr = ','.join(fieldstrlist)
        objstrlist.append(''.join(['{',objstr,'}']))
    resultstr = ','.join(objstrlist)
    result = ''.join(['[',resultstr,']'])
    return result

def charjson(characters):
    characterlist = []
    for object in characters:
        characterproplist = [ 
            ''.join(['"name":"',object.name,'"']),
            ''.join(['"id":',str(object.id)]),
            ''.join(['"type":"',object.type.name,'"']),
            ''.join(['"chapter":"',object.chapter.name,'"']),
            ''.join(['"chapterid":',str(object.chapter.id)])
        ]
        characterstring = ''.join(['{',','.join(characterproplist),'}'])
        characterlist.append(characterstring)
    characterjson = ''.join(['[',','.join(characterlist),']'])
    return characterjson

def charinfojson(charinfo):
    charid = charinfo['character'].id
    inclanlist = ''
    if charinfo['inclanlist'] != '':
        inclanlist = ','.join(charinfo['inclanlist'])
    else:
        inclanlist = ''
    del charinfo['character']
    del charinfo['inclanlist']
    charinfolist = [u''.join([u'"character":"',unicode(charid),u'"',u'"inclanlist":"',inclanlist,u'"'])]
    for key in charinfo:
        charinfolist = u''.join([u'"',unicode(key),u'":"',unicode(charinfo[key]),u'"'])
    jcharinfo = u''.join([u'{',u','.join(charinfolist),u'}'])
    return jcharinfo

def eventjson(events):
    eventlist = []
    for object in events:
        eventproplist = [
            ''.join(['"id":',str(object.id)]),
            ''.join(['"name":"',object.name,'"']),
            ''.join(['"chapter":"',object.chapter.name,'"']),
            ''.join(['"chapterid":',str(object.chapter.id)]),
            ''.join(['"chapteraddress":"',object.chapteraddress.address1,' ',object.chapteraddress.city,', ',object.chapteraddress.state,' ',object.chapteraddress.zip,'"']),
            '"maplink":""',
            ''.join(['"dateheld":"',object.dateheld.strftime('%m/%d/%Y'),'"'])
        ]
        eventstring = ''.join(['{',','.join(eventproplist),'}'])
        eventlist.append(eventstring)
    eventjson = ''.join(['[',','.join(eventlist),']'])
    return eventjson

def chapterjson(chapters):
    chapterlist = []
    for object in chapters:
        chapterproplist = [
            ''.join(['"id":',str(object.id)]),
            ''.join(['"name":"',object.name,'"']),
            ''.join(['"type":"',object.type.name,'"']),
        ]
        chapterstring = ''.join(['{',','.join(chapterproplist),'}'])
        chapterlist.append(chapterstring)
    chapterjson = ''.join(['[',','.join(chapterlist),']'])
    return chapterjson

def traitjson(traits):
    traitlist = []
    for object in traits:
        traitproplist = [
            ''.join(['"id":',str(object.id)]),
            ''.join(['"name":"',object.name,'"']),
            ''.join(['"type":"',object.type.name,'"']),
        ]
        traitstring = ''.join(['{',','.join(traitproplist),'}'])
        traitlist.append(traitstring)
    traitjson = ''.join(['[',','.join(traitlist),']'])
    return traitjson

def atraitjson(nlist,charinfo):
    if not nlist:
        return '[]'
    character = charinfo['character']
    typelist = {}
    traitlist = []
    generation = int(charinfo['generation'])
    merittotal = calcmerit(character)
    fcount = 0
    flawtype = TraitType.objects.activeonly().get(name='Flaw')
    flaws = Trait.objects.activeonly().filter(type=flawtype)
    charflaws = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=flaws).filter(isfree=False)
    for object in charflaws:
        fcount = fcount + object.trait.level
    for object in nlist:
        totalcount = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=object).count() + 1
        inclans = getcharinclanidlist(character)
        isoutofclan = 0
        xpcost = 0
        if object.type.name == 'Discipline':
            istraitinclan = isinclan(character,object)
            if not istraitinclan:
                isoutofclan = 1
        if object.type.name in ['Path']:
            charinfo = getcharinfo(character)
            xpcost = addtrait(charinfo=charinfo,trait=object,iscreation=True,isfree=True,authorizedby=None,number=1,calculateonly=True,tryonly=False)
        elif object.type.name in ['Bloodline']:
            charinfo = getcharinfo(character)
            #xpcost = addtrait(charinfo=charinfo,trait=object,iscreation=True,isfree=True,authorizedby=None,number=1,calculateonly=True,tryonly=False)
            xpcost = getraritycost(charinfo, object)
        elif object.type.name in ['Flaw']:
            xpcost = gettraitxpcost(trait=object,generation=generation,isoutofclan=isoutofclan,tcount=totalcount,fcount=fcount,date=None)
        else:
            xpcost = gettraitxpcost(trait=object,generation=generation,isoutofclan=isoutofclan,tcount=totalcount,fcount=0,date=None)
        label = gettraitlabel(character,trait=object)
        available = True
        trait = u''.join(['{"name":"',
            label.decode('utf-8'),
            u'","id":"',
            unicode(object.id),
            u'","type":"',
            object.type.name.decode('utf-8'),
            u'","isadmin":"',
            unicode(object.isadmin),
            u'","isinclan":"',
            u'False',
            u'","level":"',
            unicode(object.level),
            u'","xpcost":"',
            unicode(xpcost),
            u'","available":"',
            unicode(available),
            u'","description":"',
            object.description.decode('utf-8'),
            u'"}'
            ]).encode('utf-8')
        if object.type.name not in typelist:
            xpcost = gettypexpcost(character,object.type)
            type = {'name':object.type.name,'aggregate':object.type.aggregate,'onepercharacter':object.type.onepercharacter,'multiplyxp':object.type.multiplyxp,'xpcost':xpcost,'traits':[]}
            typelist[object.type.name] = type
        typelist[object.type.name]['traits'].append(trait)
    for item in typelist:
        typestring = u''.join(['{"name":"',
            typelist[item]['name'].encode('utf-8'),
            u'","aggregate":"',
            unicode(typelist[item]['aggregate']),
            u'","onepercharacter":"',
            unicode(typelist[item]['onepercharacter']),
            u'","traits":[',
            u','.join(typelist[item]['traits']),
            u']}',
            ])
        traitlist.append(typestring)
    atraits = u''.join(['[',','.join(traitlist),']'])
    return atraits

def chartraitjson(nlist):
    if not nlist:
        return '[]'
    typedict = {}
    traitdict = {}
    for object in nlist:
        label = gettraitlabel(character,ctrait=object)
        if object.trait.type.name not in typedict:
            type = {'name':object.trait.type.name,'aggregate':object.trait.type.aggregate,'onepercharacter':object.trait.type.onepercharacter,'count':0,'traits':{}}
            typedict[object.trait.type.name] = type
        if label not in typedict[object.trait.type.name]['traits']:
            trait = {'name':label,'id':object.trait.id,'type':object.trait.type.name,'isadmin':object.trait.isadmin,'level':object.trait.level,'count':1,'latestid':object.id,'description':object.trait.description}
            typedict[object.trait.type.name]['traits'][label] = trait
        else:
            typedict[object.trait.type.name]['traits'][label]['count'] = typedict[object.trait.type.name]['traits'][label]['count']+1
            typedict[object.trait.type.name]['traits'][label]['latestid'] = object.id
        traitcount = CharacterTrait.objects.activeonly().filter(character=object.character).filter(trait=object.trait).count()
        typedict[object.trait.type.name]['count'] = typedict[object.trait.type.name]['count'] + 1
    typelist = []
    for item in typedict:
        traitlist = []
        for trait in typedict[item]['traits']:
            traitlist.append(''.join(['{"name":"',
                typedict[item]['traits'][trait]['name'],
                '","id":"',
                str(typedict[item]['traits'][trait]['id']),
                '","type":"',
                typedict[item]['traits'][trait]['type'],
                '","isadmin":"',
                str(typedict[item]['traits'][trait]['isadmin']),
                '","level":"',
                str(typedict[item]['traits'][trait]['level']),
                '","description":"',
                typedict[item]['traits'][trait]['description'],
                '","count":"',
                str(typedict[item]['traits'][trait]['count']),
                '","latestid":"',
                str(typedict[item]['traits'][trait]['latestid']),
                '"}'
            ]))
        typelist.append(''.join(['{"name":"',
            typedict[item]['name'],
            '","aggregate":"',
            str(typedict[item]['aggregate']),
            '","onepercharacter":"',
            str(typedict[item]['onepercharacter']),
            '","count":"',
            str(typedict[item]['count']),
            '","traits":[',
            ','.join(traitlist),
            ']}'
        ]))
    ctraits = ''.join(['[',','.join(typelist),']'])
    return ctraits

def ctraitjson(nlist):
    if not nlist:
        return '[]'
    typedict = {}
    traitdict = {}
    character = nlist[0].character
    for object in nlist:
        label = gettraitlabel(character,ctrait=object)
        if object.trait.type.name not in typedict:
            if object.isfree == False:
                gettypexpcost(object.character,object.trait.type,object.dateactive)
            type = {'name':object.trait.type.name,'aggregate':object.trait.type.aggregate,'onepercharacter':object.trait.type.onepercharacter,'xpcost':0,'count':0,'traits':{}}
            typedict[object.trait.type.name] = type
        if label not in typedict[object.trait.type.name]['traits']:
            trait = {'name':label,'id':object.trait.id,'type':object.trait.type.name,'isadmin':object.trait.isadmin,'level':object.trait.level,'count':1,'xpcost':0,'latestid':object.id,'description':object.trait.description}
            typedict[object.trait.type.name]['traits'][label] = trait
        else:
            typedict[object.trait.type.name]['traits'][label]['count'] = typedict[object.trait.type.name]['traits'][label]['count']+1
            typedict[object.trait.type.name]['traits'][label]['latestid'] = object.id
        traitcount = CharacterTrait.objects.activeonly().filter(character=object.character).filter(trait=object.trait).count()
        typedict[object.trait.type.name]['count'] = typedict[object.trait.type.name]['count'] + 1
    typelist = []
    for item in typedict:
        traitlist = []
        for trait in typedict[item]['traits']:
            traitlist.append(''.join(['{"name":"',
                typedict[item]['traits'][trait]['name'],
                '","id":"',
                str(typedict[item]['traits'][trait]['id']),
                '","type":"',
                typedict[item]['traits'][trait]['type'],
                '","isadmin":"',
                str(typedict[item]['traits'][trait]['isadmin']),
                '","level":"',
                str(typedict[item]['traits'][trait]['level']),
                '","description":"',
                typedict[item]['traits'][trait]['description'],
                '","xpcost":"',
                str(typedict[item]['traits'][trait]['xpcost']),
                '","count":"',
                str(typedict[item]['traits'][trait]['count']),
                '","latestid":"',
                str(typedict[item]['traits'][trait]['latestid']),
                '"}'
            ]))
        typelist.append(''.join(['{"name":"',
            typedict[item]['name'],
            '","aggregate":"',
            str(typedict[item]['aggregate']),
            '","onepercharacter":"',
            str(typedict[item]['onepercharacter']),
            '","xpcost":"',
            str(typedict[item]['xpcost']),
            '","count":"',
            str(typedict[item]['count']),
            '","traits":[',
            ','.join(traitlist),
            ']}'
        ]))
    ctraits = ''.join(['[',','.join(typelist),']'])
    return ctraits

def ptraitjson(nlist):
    if not nlist:
        return '[]'
    typedict = {}
    traitdict = {}
    character = nlist[0].character
    generation = int(getchargen(character)['generation'])
    for object in nlist:
        label = gettraitlabel(character,ctrait=object)
        totalcount = 0
        if object.trait.type.aggregate == True:
            totalcount = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=object.trait).filter(dateactive__lt=object.dateactive).count() + 1
        isoutofclan = 0
        if object.trait.type.name == 'Discipline':
            istraitinclan = isinclan(character,object.trait)
            if istraitinclan == False:
                isoutofclan = 1
        xpcost = gettraitxpcost(trait=object.trait,generation=generation,isoutofclan=isoutofclan,tcount=totalcount,fcount=0,date=None)
        if object.trait.type.name not in typedict:
            typexpcost = gettypexpcost(character,object.trait.type)
            type = {'id':object.trait.type.id,'name':object.trait.type.name,'aggregate':object.trait.type.aggregate,'onepercharacter':object.trait.type.onepercharacter,'xpcost':typexpcost,'count':0,'traits':{}}
            typedict[object.trait.type.name] = type
        authorizedbyname = 'None'
        if object.authorizedby != None:
            authorizedbyname = object.authorizedby.username
        trait = {'name':label,'id':object.trait.id,'type':object.trait.type.name,'isadmin':object.trait.isadmin,'level':object.trait.level,'count':totalcount,'xpcost':xpcost,'latestid':object.id,'authorizedby':authorizedbyname,'description':object.trait.description}
        typedict[object.trait.type.name]['traits'][object.id] = trait
        typedict[object.trait.type.name]['count'] = totalcount
    typelist = []
    for item in typedict:
        traitlist = []
        for trait in typedict[item]['traits']:
            traitlist.append(''.join(['{"name":"',
                typedict[item]['traits'][trait]['name'],
                '","id":"',
                str(typedict[item]['traits'][trait]['id']),
                '","type":"',
                typedict[item]['traits'][trait]['type'],
                '","isadmin":"',
                str(typedict[item]['traits'][trait]['isadmin']),
                '","level":"',
                str(typedict[item]['traits'][trait]['level']),
                '","description":"',
                typedict[item]['traits'][trait]['description'],
                '","xpcost":"',
                str(typedict[item]['traits'][trait]['xpcost']),
                '","count":"',
                str(typedict[item]['traits'][trait]['count']),
                '","latestid":"',
                str(typedict[item]['traits'][trait]['latestid']),
                '","authorizedby":"',
                str(typedict[item]['traits'][trait]['authorizedby']),
                '"}'
            ]))
        typelist.append(''.join(['{"name":"',
            typedict[item]['name'],
            '","aggregate":"',
            str(typedict[item]['aggregate']),
            '","onepercharacter":"',
            str(typedict[item]['onepercharacter']),
            '","xpcost":"',
            str(typedict[item]['xpcost']),
            '","count":"',
            str(typedict[item]['count']),
            '","traits":[',
            ','.join(traitlist),
            ']}'
        ]))
    ptraits = ''.join(['[',','.join(typelist),']'])
    return ptraits

def ltraitjson(nlist):
    if not nlist:
        return '[]'
    typedict = {}
    traitlist = []
    character = nlist[0].character
    generation = int(getchargen(character)['generation'])
    for object in nlist:
        label = gettraitlabel(character,ctrait=object)
        totalcount = 0
        if object.trait.type.aggregate == True and object.dateactive != None:
            totalcount = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=object.trait).filter(dateactive__lt=object.dateactive).count() + 1
        xpcost = 0
        isoutofclan = 0
        if object.trait.type.name == 'Discipline' and object.isfree == False:
            istraitinclan = isinclan(character,object.trait)
            if istraitinclan == False:
                isoutofclan = 1
        if object.isfree == False:
            xpcost = gettraitxpcost(trait=object.trait,generation=generation,isoutofclan=isoutofclan,tcount=totalcount,fcount=0,date=None)
        authorizedbyname = None
        authorizedbyid = 0
        if object.authorizedby:
            authorizedbyname = object.authorizedby.username
            authorizedbyid = object.authorizedby.id        
        trait = {'name':object.trait.name,
            'label':label,
            'id':object.trait.id,
            'type':object.trait.type.name,
            'isadmin':object.trait.isadmin,
            'level':object.trait.level,
            'count':1,
            'xpcost':xpcost,
            'iscreation':object.iscreation,
            'isfree':object.isfree,
            'latestid':object.id,
            'description':object.trait.description,
            'dateactive':object.dateactive,
            'dateexpiry':object.dateexpiry,
            'dateremoved':object.dateremoved,
            'dateauthorized':object.dateauthorized,
            'authorizedby':authorizedbyname,
            'authorizedbyid':authorizedbyid
        }
        traitlist.append(trait)
    jsonlist = []
    for item in traitlist:
        dateactivestr = formatanydate(item['dateactive'],'USHMS')
        dateexpirystr = formatanydate(item['dateexpiry'],'USHMS')
        dateremovedstr = formatanydate(item['dateremoved'],'USHMS')
        jsonlist.append(''.join(['{"name":"',
            item['name'],
            '","id":"',
            unicode(item['id']),
            '","type":"',
            item['type'],
            '","isadmin":"',
            unicode(item['isadmin']),
            '","level":"',
            unicode(item['level']),
            '","description":"',
            item['description'],
            '","xpcost":"',
            unicode(item['xpcost']),
            '","iscreation":"',
            unicode(item['iscreation']),
            '","isfree":"',
            unicode(item['isfree']),
            '","latestid":"',
            unicode(item['latestid']),
            '","dateactive":"',
            dateactivestr,
            '","dateexpiry":"',
            dateexpirystr,
            '","dateremoved":"',
            dateremovedstr,
            '","dateauthorized":"',
            unicode(item['dateauthorized']),
            '","authorizedby":"',
            unicode(item['authorizedby']),
            '","authorizedbyid":"',
            unicode(item['authorizedbyid']),
            '"}'
        ]))
    ltraits = ''.join(['[',','.join(jsonlist),']'])
    return ltraits

def getcharsheet(charinfo,date=None):
    character = charinfo['character']
    del charinfo['character']
    charinfo['character'] = character.id
    charactertraits = CharacterTrait.objects.showonly(date).filter(character=character)
    charsheet = {'charinfo':charinfo,'data':{}}
    for object in charactertraits:
        label = gettraitlabel(character,ctrait=object)
        if object.trait.type.name not in charsheet['data']:
            charsheet['data'][object.trait.type.name] = {
                'name':object.trait.type.name,
                'count':1,
                'typeid':object.trait.type.id,
                'traits':{},
                }
        else:
            charsheet['data'][object.trait.type.name]['count'] = charsheet['data'][object.trait.type.name]['count'] + 1
        if object.trait.name not in charsheet['data'][object.trait.type.name]['traits']:
            charsheet['data'][object.trait.type.name]['traits'][object.trait.name] = {
                'name':object.trait.name,
                'label':label,
                'count':1,
                'traitid':object.trait.id,
                'chartraits':[],
                }
        else:
           charsheet['data'][object.trait.type.name]['traits'][object.trait.name]['count'] = charsheet['data'][object.trait.type.name]['traits'][object.trait.name]['count'] + 1
        charsheet['data'][object.trait.type.name]['traits'][object.trait.name]['chartraits'].append(object.id)
    return simplejson.dumps(charsheet, ensure_ascii=False)
        

def getidlist(nmodel):
    idlist = []
    for object in nmodel:
        idlist.append(object.id)
    return idlist

def getdate(date=None,time=None):
    if time == None:
        time = '0000'
    if date == None:
        date = datetime.now()
    else:
        date = datetime(year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]), hour=int(time[0:2]), minute=int(time[2:4]))
    return date

def getdatefromstr(ndate=None,ntime=None):
    todaydate = datetime.now()
    if ntime == None:
        ntime = formatanydate(todaydate, 'militarytime')
    if ndate == None:
        ndate = formatanydate(todaydate,'flatstr')
    date = datetime(year=int(ndate[0:4]), month=int(ndate[4:6]), day=int(ndate[6:8]), hour=int(ntime[0:2]), minute=int(ntime[2:4]))
    return date

def gridformat(infodict,traits,traittypes):
    info = {}
    for object in infodict:
        info[object] = ''.join(['<td><b>',object,':</b>&nbsp;',infodict[object],'</td>'])
    infoitems = ['<tr>']
    infoitems.append(info['name'])
    infoitems.append(info['owner'])
    infoitems.append('</tr><tr>')
    infoitems.append(info['Clan'])
    infoitems.append(info['Archetype'])
    infoitems.append('</tr>')
    grid = {}
    for traittype in traittypes:
        type = traittype['name']
        griditems = []
        if type != 'Emphasis':
            griditems = [''.join(['<td><b>',type,'</b><br/>'])]
            for traitvalue in traits:
                trait = traitvalue['name']
                if traitvalue['type'] == type:
                    emphasis = ''
                    for e in traits:
                        if e['type'] == 'Emphasis' and e['name'] == trait:
                            emphasis = '*'
                    count = ''
                    if traittype['aggregate'] == 'True':
                        count = str(traitvalue['count'])
                    griditems.extend([emphasis,trait,'&nbsp;',count,'<br/>'])
            griditems.append(''.join(['</td>']))
        grid[type] = ''.join(griditems)
    items = []
    items.extend(infoitems)
    items.append('<tr>')
    items.append(grid['Temper'])
    items.append(grid['Attribute'])
    items.append(grid['Status'])
    items.append('</tr><tr>')
    items.append(grid['Skill'])
    items.append(grid['Background'])
    items.append(grid['Discipline'])
    items.append('</tr></tr>')
    items.append(grid['Merit'])
    items.append(grid['Flaw'])
    items.append('</tr>')
    value = ''.join(items)
    return value

def getcharlist(user,nviewname,event=None,date=None):
    statetype = TraitType.objects.activeonly(date).filter(name='State')
    owned_list = []
    if nviewname == 'st':
        approvers = StaffType.objects.activeonly(date).filter(isapprover=True)
        stafflist = Staff.objects.activeonly(date).filter(type__in=approvers).filter(user=user)
        chapter_list = []
        for object in stafflist:
            chapter_list.append(object.chapter.id)
        chapcharacters = Character.objects.activeonly(date).filter(chapter__in=chapter_list)
        for object in chapcharacters:
            owned_list.append(object.id)
        statelist = ['Pending','Active']
    elif nviewname == 'owned':
        owners = CharacterOwner.objects.activeonly(date).filter(user=user).filter(iscontroller=True)
        for object in owners:
            owned_list.append(object.character.id)
        statelist = ['New','Pending','Active']
    elif nviewname == 'active':
        owners = CharacterOwner.objects.activeonly(date).filter(user=user).filter(iscontroller=True)
        for object in owners:
            owned_list.append(object.character.id)
        statelist = ['Active']
    elif nviewname == 'event':
        if event == None:
            chapcharacters = Character.objects.activeonly(date)
        else:
            chapcharacters = Character.objects.activeonly(date).filter(chapter=event.chapter)
        for object in chapcharacters:
            owned_list.append(object.id)
        statelist = ['Active']
    elif nviewname == 'allactive':
        characters = Character.objects.activeonly(date)
        for object in characters:
            owned_list.append(object.id)
        statelist = ['Active']
    else:
        return None
    ownedcharacters = Character.objects.activeonly(date).filter(pk__in=owned_list)
    charid_list = []
    for object in ownedcharacters:
        charstate = getcharstate(object)
        if charstate['state'] in statelist:
            charid_list.append(object.id)
    characters = Character.objects.activeonly(date).filter(pk__in=charid_list)
    return characters  

def getchaptercharlist(chapter,showinactive=False):
    statetype = TraitType.objects.activeonly().get(name='State')
    hiddentrait = Trait.objects.activeonly().filter(type=statetype).get(name='Hidden')
    hiddenchartraits = CharacterTrait.objects.filter(trait=hiddentrait)
    hiddencharidlist = []
    for object in hiddenchartraits:
        hiddencharidlist.append(object.character.id)
    chapcharacters = Character.objects.activeonly().filter(chapter=chapter).exclude(pk__in=hiddencharidlist)
    return chapcharacters

def getchapterlist(user,nviewname=None,date=None):
    if nviewname == 'st':
        approvers = StaffType.objects.activeonly(date).filter(isapprover=True)
        stafflist = Staff.objects.activeonly(date).filter(type__in=approvers).filter(user=user)
        chapter_list = []
        for object in stafflist:
            chapter_list.append(object.chapter.id)
        chapters = Chapter.objects.activeonly(date).filter(pk__in=chapter_list)
    else:
        chapters = Chapter.objects.activeonly(date)
    return chapters

def getchartiles(nviewname=None,chapter=None,user=None,state=None,allstates=None):
    q = Q(pk__gte=0)
    if chapter == None:
        return None
    if nviewname == 'director':
        characters = Character.objects.filter(chapter=chapter)
    elif nviewname == 'st':
        characters = Character.objects.filter(chapter=chapter) 
    elif nviewname == 'owner':
        if user == None:
            return None
        else:
            owners = CharacterOwner.objects.activeonly().filter(user=user)
            charidlist = []
            for object in owners:
                if object.character.chapter == chapter:
                    charidlist.append(object.character.id)
            characters = Character.objects.filter(pk__in=charidlist)
    elif nviewname == 'favorite':
        if user == None:
            return None
        else:
            favorites = FavoriteCharacter.objects.activeonly().filter(user=user)
            charidlist = []
            for object in favorites:
                if object.character.chapter == chapter:
                    charidlist.append(object.character.id)
    else:
        return None
    if state == None:
        return None
    charlist = []
    t=1
    for object in characters:
        charstates = CharacterTrait.objects.filter(character=object).filter(trait__in=allstates)
        if charstates.count() > 0:
            charstate = charstates.order_by('-dateactive')[0].trait.name
            if charstate == state.name:
                if t>5:
                    t=1
                owner = ''
                owners = getcharowners(object)
                if owners:
                    ownerprofile = UserProfile.objects.get(user=owners[0].user)
                    owner = ownerprofile.name
                charlist.append({'name':str(object.name.replace("'","\'")), 'owner':owner, 'state':charstate, 'link':''.join(['/characters/',str(object.id),'/']),'left':t*20})
                t=t+1
    return charlist

def getuserinfo(user,action=None):
    if not user:
        return None
    storytellers = [] 
    for object in StaffType.objects.activeonly().filter(isapprover=True):
        storytellers.append(object.id)
    directors = []
    for object in StaffType.objects.activeonly().filter(isdirector=True):
        directors.append(object.id)
    st = Staff.objects.activeonly().filter(user=user).filter(type__in=StaffType.objects.activeonly().filter(isapprover=True))
    isdirector = Staff.objects.activeonly().filter(type__in=directors).filter(user=user).exists()
    profile = UserProfile.objects.get(user=user)
    subscriptions = Subscription.objects.activeonly().filter(user=user)
    upgrade = Vocabulary.objects.get(name="Upgrade").displayname
    dbversion = Vocabulary.objects.get(name="DBVersion").displayname
    announcement = Vocabulary.objects.get(name="Announcement").displayname
    if subscriptions:
        subscription = True
    else:
        subscription = False
    userinfo = {'userid':user.id
        , 'username':user.username
        , 'email':user.email
        , 'isadmin':profile.isadmin
        , 'isst':st.exists()
        , 'isdirector':isdirector
        , 'subscription':subscription
        , 'acceptedterms':profile.acceptedterms
        , 'name':profile.name
        , 'upgrade':upgrade
        , 'dbversion':dbversion
        , 'announcement':announcement
    }
    return userinfo

def gettraitlabel(character,ctrait=None,trait=None,date=None):
    label = None
    if ctrait:
        if ctrait.label is not None and ctrait.trait.name != ctrait.label:
            label = ctrait.label
        else:
            trait = ctrait.trait
    if trait:
        traitlabel = TraitLabel.objects.activeonly(date).filter(character=character).filter(trait=trait)
        if traitlabel.count() > 0:
            label = traitlabel.order_by('-dateactive')[0].label
        else:
            label = trait.name
    return label 

def gettraitrename(charactertrait,date):
    rename = TraitRename.objects.activeonly(date).filter(chracter=charactertrait.character).filter(charactertrait=charactertrait)
    if rename.count() > 0:
        return rename.order_by('-dateactive')[0].rename
    else:
        return charactertrait.trait.name

def gettraitsbytype(ntypename,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    traits = Trait.objects.activeonly(date).filter(type=traittype)
    return traits

def gettraitbyname(ntypename,ntraitname,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    trait = Trait.objects.activeonly(date).filter(type=traittype).get(name=ntraitname)
    return trait

def getchartraitsbytype(character,ntypename,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    traits = Trait.objects.activeonly(date).filter(type=traittype)
    traitidlist = getidlist(traits)
    chartraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=traitidlist)
    return chartraits

def getchartraitsbyname(character,ntypename,ntraitname,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    trait = Trait.objects.activeonly(date).filter(type=traittype).get(name=ntraitname)
    chartraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=trait)
    return chartraits

def getcharsheettraitsbytype(character,ntypename,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    traits = Trait.objects.activeonly(date).filter(type=traittype)
    traitidlist = getidlist(traits)
    chartraits = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait__in=traitidlist)
    return chartraits

def getcharsheettraitsbyname(character,ntypename,ntraitname,date=None):
    traittype = TraitType.objects.activeonly(date).get(name=ntypename)
    trait = Trait.objects.activeonly(date).filter(type=traittype).get(name=ntraitname)
    chartraits = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait=trait)
    return chartraits

def getchartraitcount(character,trait,date=None):
    chartraitcount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=trait).count()
    return chartraitcount

def getcharsheettraitcount(character,trait,date=None):
    chartraitcount = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait=trait).count()
    return chartraitcount

def getchartraittypecount(character,ntypename,date=None):
    traits = gettraitsbytype(ntypename,date)
    chartraitcount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=traits).count()
    return chartraitcount

def getchartraitmaxlevel(character,trait=None,ntypename=None,date=None):
    traitlist = []
    if trait != None:
        traitlist = [trait.id]
    if ntypename != None:
        traittype = TraitType.objects.activeonly(date).get(name=ntypename)
        traits = Trait.objects.activeonly(date).filter(type=traittype)
        for object in traits:
            traitlist.append(object.id)
    chartraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=traitlist)
    maxlevel = 0
    for object in chartraits:
        if object.trait.level > maxlevel:
            maxlevel = object.trait.level
    return maxlevel

def getcharsteps(character,date=None):
    steptype = TraitType.objects.activeonly().get(name='Step Complete')
    steps = Trait.objects.activeonly().filter(type=steptype)
    charsteptraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=steps)
    charsteps = {'Step1':'false',
        'Step2':'false',
        'Step3':'false',
        'Step4':'false',
        'Step5':'false',
        'Step6':'false',
        'Step7':'false',
    }
    for object in charsteptraits:
        charsteps[object.trait.name.replace(' ','')] = 'true'
    return charsteps

def getchargen(character,date=None):
    chargen = {'character':character,'generation':'0'}
    generationtrait = gettraitbyname('Background','Generation',date)
    generation = getchartraitcount(character,generationtrait,date)
    if generation:
        if generation > 5:
            generation = 5
        chargen['generation'] = str(generation)
    return chargen

def getcharclan(character,date=None):
    charclan = {'clan':'','bloodline':'','sect':''}
    clans = gettraitsbytype('Clan',date)
    bloodlines = gettraitsbytype('Bloodline',date)
    sects = gettraitsbytype('Sect',date)
    chartraitclan = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=clans).order_by('-dateactive')
    chartraitbloodline = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=bloodlines).order_by('-dateactive')
    chartraitsect = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=sects).order_by('-dateactive')
    if chartraitclan:
        charclan['clan'] = chartraitclan[0].trait.name
    if chartraitbloodline:
        charclan['bloodline'] = chartraitbloodline[0].trait.name
    if chartraitsect:
        charclan['sect'] = chartraitsect[0].trait.name
    return charclan

def getcharstate(character,date=None):
    charstate = {'state':'','priority':'','statedate':'','statedatetime':''}
    ttypes = TraitType.objects.activeonly(date).filter(name__in=['State','Priority'])
    traits = Trait.objects.activeonly(date).filter(type__in=ttypes)
    states = traits.filter(type=ttypes.get(name='State'))
    priorities = traits.filter(type=ttypes.get(name='Priority'))
    ctraits = CharacterTrait.objects.filter(character=character).filter(trait__in=traits)
    cstates = ctraits.filter(trait__in=states)
    if cstates.count() > 0:
        charstate['state'] = cstates.order_by('-dateactive')[0].trait.name
        charstate['statedate'] = formatanydate(cstates.order_by('-dateactive')[0].dateactive)
        charstate['statedatetime'] = formatanydate(cstates.order_by('-dateactive')[0].dateactive,'url')
    cpriorities = ctraits.filter(trait__in=priorities)
    if cpriorities:
        charstate['priority'] = cpriorities.order_by('-dateactive')[0].trait.name
    return charstate

def getchartemper(character,generation,date=None):
    chartemper = {'blood':'0','bloodper':'0','willpower':'6','path':'Humanity','pathlevel':'0'}
    if generation > 5:
        generation = 5
    bloodlist = [[0,0],[10,1],[12,2],[15,3],[20,4],[30,5]]
    chartemper['blood'] = unicode(bloodlist[generation][0])
    chartemper['bloodper'] = unicode(bloodlist[generation][1])
    specialtype = TraitType.objects.activeonly().get(name='Special')
    exhausted = Trait.objects.activeonly().filter(type=specialtype).get(name='Exhausted')
    charexhausted = CharacterTrait.objects.showonly().filter(character=character).filter(trait=exhausted)
    charunyielding = getchartraitsbyname(character,'Merit','Unyielding',date)
    chartemper['willpower'] = unicode(6 - charexhausted.count() + charunyielding.count())
    charrugged = getchartraitsbyname(character,'Merit','Rugged')
    charstamina = getchartraitsbyname(character,'Physical Focus','Stamina')
    charfort = getchartraitsbyname(character,'Discipline','Fortitude')
    charhealth = 3
    if charrugged.count() > 0:
        charhealth = charhealth + 1
    if charstamina.count() > 0 and charfort.count() > 0:
        charhealth = charhealth + 1
    chartemper['health'] = unicode(charhealth)
    paths = gettraitsbytype('Path',date)
    chartraitpath = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait__in=paths).order_by('-dateactive')
    morality = gettraitbyname('Morality','Morality',date)
    moralitylevel = getcharsheettraitcount(character,morality,date)
    if chartraitpath:
        chartemper['path'] = chartraitpath[0].trait.name
    chartemper['pathlevel'] = unicode(moralitylevel)
    return chartemper

def getcharmagic(character,date=None):
    disctype = TraitType.objects.activeonly(date).get(name='Discipline')
    magictype = TraitType.objects.activeonly(date).get(name='Primary Magic')
    #Find Primary Necromancy
    primarynecrotraits = Trait.objects.activeonly(date).filter(type=magictype).filter(name__contains='Necromancy')
    charprimarynecro = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=primarynecrotraits)
    primarynecro = ''
    primarynecrocount = 0
    if charprimarynecro:
        primarynecrotrait = charprimarynecro.order_by('dateactive')[0].trait
        primarynecro = primarynecrotrait.name
        primarynecrodisc = Trait.objects.activeonly(date).filter(type=disctype).filter(name=primarynecrotrait.name)
        primaryncerocount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=primarynecrodisc).count()
    #Find Primary Thaumaturgy
    primarythaumtraits = Trait.objects.activeonly(date).filter(type=magictype).filter(name__contains='Thaumaturgy')
    charprimarythaum = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=primarythaumtraits)
    primarythaum = ''
    primarythaumcount = 0
    if charprimarythaum:
        primarythaumtrait = charprimarythaum.order_by('dateactive')[0].trait
        primarythaum = primarythaumtrait.name
        primarythaumdisc = Trait.objects.activeonly(date).filter(type=disctype).filter(name=primarythaumtrait.name)
        primarythaumcount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=primarythaumdisc).count()
    return {'primarynecro':primarynecro,'primarynecrocount':unicode(primarynecrocount),'primarythaum':primarythaum,'primarythaumcount':unicode(primarythaumcount)}

def getcharsheetinfo(character,date=None):
    hasspecializations = False
    haselderpowers = False
    hastechniques = False
    hasnecro = False
    hasthaum = False
    specialtype = TraitType.objects.activeonly(date).get(name='Special')
    specialtraits = Trait.objects.activeonly(date).filter(type=specialtype).filter(Q(name__contains='Specialization'))
    specializations = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait__in=specialtraits)
    elderpowers = getcharsheettraitsbytype(character,'Elder Power',date)
    techniques = getcharsheettraitsbytype(character,'Technique',date)
    necro = getcharsheettraitsbytype(character,'Necromantic Ritual',date)
    thaum = getcharsheettraitsbytype(character,'Thaumaturgical Ritual',date)
    if specializations.count() > 0:
        hasspecializations = True
    if elderpowers.count() > 0:
        haselderpowers = True
    if techniques.count() > 0:
        hastechniques = True
    if necro.count() > 0:
        hasnecro = True
    if thaum.count() > 0:
        hasthaum = True
    charsheetinfo = {
        'hasspecializations':unicode(hasspecializations),
        'haselderpowers':unicode(haselderpowers),
        'hastechniques':unicode(hastechniques),
        'hasnecro':unicode(hasnecro),
        'hasthaum':unicode(hasthaum)
        }
    return charsheetinfo

def getcharinfo(character,date=None):
    if not character:
        return None
    charinfo = {}
    xptotals = calcXP(character,date)
    ttypes = TraitType.objects.activeonly()
    atraits = Trait.objects.activeonly()
    states = atraits.filter(type=ttypes.get(name='State'))
    priorities = atraits.filter(type=ttypes.get(name='Priority'))
    actraits = CharacterTrait.objects.filter(character=character).filter(Q(trait__in=states)|Q(trait__in=priorities))
    ctraits = CharacterTrait.objects.showonly().filter(character=character)
    charinfo['character'] = character
    charinfo['name'] = character.name
    charinfo['type'] = character.type.name
    charinfo['typeid'] = character.type.id
    charinfo['id'] = character.id
    charinfo['chapter'] = character.chapter.name
    charinfo['chapterid'] = character.chapter.id
    charinfo['chaptertype'] = character.chapter.type.name
    charinfo['private'] = character.private_description
    charinfo['public'] = character.public_description
    charinfo['xpearned'] = xptotals['xptotal']
    charinfo['xpspent'] = xptotals['xpspent']
    charinfo['xpremaining'] = xptotals['xptotal'] - xptotals['xpspent']
    merittotal = 0
    cmerits = ctraits.filter(trait__in=atraits.filter(type=ttypes.get(name='Merit'))).filter(isfree=False)
    for cmerit in cmerits:
        merittotal = merittotal + cmerit.trait.level
    charinfo['meritspent'] = str(merittotal)
    charinfo['meritremaining'] = str(7 - merittotal)
    charinfo['primarythaum'] = ''
    charinfo['primarynecro'] = ''
    charinfo['primarythaumcount'] = '0'
    charinfo['primarynecrocount'] = '0'
    charinfo['owner'] = ''
    charinfo['ownerid'] = ''
    charinfo['player'] = ''
    cstate = 'New'
    cstatedate = ''
    cstatedatetime = ''
    cstates = actraits.filter(trait__in=states)
    if cstates.count() > 0:
        cstate = cstates.order_by('-dateactive')[0].trait.name
        cstatedate = cstates.order_by('-dateactive')[0].trait.name
        cstatedatetime = cstates.order_by('-dateactive')[0].trait.name
    charinfo['state'] = cstate
    charinfo['statedate'] = cstatedate
    charinfo['statedatetime'] = cstatedatetime
    charinfo['priority'] = 'Secondary'
    cpriorities = actraits.filter(trait__in=priorities)
    if cpriorities.count() > 0:
        charinfo['priority'] = cpriorities.order_by('-dateactive')[0].trait.name
    charinfo['clan'] = ''
    cclans = ctraits.filter(trait__in=atraits.filter(type=ttypes.get(name='Clan')))
    if cclans.count() > 0:
        charinfo['clan'] = cclans.order_by('-dateactive')[0].trait.name
    charinfo['bloodline'] = ''
    cbloodlines = ctraits.filter(trait__in=atraits.filter(type=ttypes.get(name='Bloodline')))
    if cbloodlines.count() > 0:
        charinfo['bloodline'] = cbloodlines.order_by('-dateactive')[0].trait.name
    charinfo['sect'] = ''
    csects = ctraits.filter(trait__in=atraits.filter(type=ttypes.get(name='Sect')))
    if csects.count() > 0:
        charinfo['sect'] = csects.order_by('-dateactive')[0].trait.name
    charinfo['generation'] = '1'
    cgen = ctraits.filter(trait=atraits.filter(type=ttypes.get(name='Background')).get(name='Generation'))
    if cgen.count() > 5:
        charinfo['generation'] = '5'
    elif cgen.count() > 0:
        charinfo['generation'] = unicode(cgen.count())
    chartemper = getchartemper(character,int(charinfo['generation']),date)
    charinfo['blood'] = chartemper['blood']
    charinfo['bloodper'] = chartemper['bloodper']
    charinfo['willpower'] = chartemper['willpower']
    charinfo['health'] = chartemper['health']
    charinfo['path'] = chartemper['path']
    charinfo['pathlevel'] = chartemper['pathlevel']
    charinfo['inclanlist'] = getinitialdisciplines(charinfo['clan'],charinfo['bloodline'])
    charsheetinfo = getcharsheetinfo(character,date)
    charinfo['hasspecializations'] = charsheetinfo['hasspecializations']
    charinfo['haselderpowers'] = charsheetinfo['haselderpowers']
    charinfo['hastechniques'] = charsheetinfo['hastechniques']
    charinfo['hasnecro'] = charsheetinfo['hasnecro']
    charinfo['hasthaum'] = charsheetinfo['hasthaum']
    #populate
    charmagic = getcharmagic(character,date)
    charinfo['primarythaum'] = charmagic['primarythaum']
    charinfo['primarynecro'] = charmagic['primarynecro']
    charinfo['primarythaumcount'] = charmagic['primarythaumcount']
    charinfo['primarynecrocount'] = charmagic['primarynecrocount']
    owners = getcharowners(character, date)
    if owners:
        charinfo['owner'] = owners[0].user.username
        charinfo['ownerid'] = unicode(owners[0].id)
        charinfo['player'] = owners[0].user.username
    return charinfo

def getcharinfo2(character,date=None):
    if not character:
        return None
    charinfo = {}
    xptotals = calcXP(character,date)
    merittotal = calcmerit(character,date)
    charinfo['character'] = character
    charinfo['name'] = character.name
    charinfo['type'] = character.type.name
    charinfo['typeid'] = character.type.id
    charinfo['id'] = character.id
    charinfo['chapter'] = character.chapter.name
    charinfo['chapterid'] = character.chapter.id
    charinfo['chaptertype'] = character.chapter.type.name
    charinfo['private'] = character.private_description
    charinfo['public'] = character.public_description
    charinfo['xpearned'] = xptotals['xptotal']
    charinfo['xpspent'] = xptotals['xpspent']
    charinfo['xpremaining'] = xptotals['xptotal'] - xptotals['xpspent']
    charinfo['meritspent'] = str(merittotal)
    charinfo['meritremaining'] = str(7 - merittotal)
    charinfo['primarythaum'] = ''
    charinfo['primarynecro'] = ''
    charinfo['primarythaumcount'] = '0'
    charinfo['primarynecrocount'] = '0'
    charinfo['owner'] = ''
    charinfo['ownerid'] = ''
    charinfo['player'] = ''
    charinfo['state'] = ''
    charinfo['statedate'] = ''
    charinfo['statedatetime'] = ''
    charinfo['priority'] = ''
    charinfo['clan'] = ''
    charinfo['bloodline'] = ''
    charinfo['sect'] = ''
    charinfo['generation'] = ''
    charinfo['blood'] = ''
    charinfo['bloodper'] = ''
    charinfo['willpower'] = ''
    charinfo['health'] = ''
    charinfo['path'] = ''
    charinfo['pathlevel'] = ''
    charinfo['inclanlist'] = []
    charinfo['hasspecializations'] = 'False'
    charinfo['haselderpowers'] = 'False'
    charinfo['hastechniques'] = 'False'
    charinfo['hasnecro'] = 'False'
    charinfo['hasthaum'] = 'False'
    #Populate
    owners = getcharowners(character, date)
    if owners:
        charinfo['owner'] = owners[0].user.username
        charinfo['ownerid'] = unicode(owners[0].id)
        charinfo['player'] = owners[0].user.username
    charstate = getcharstate(character)
    charinfo['state'] = charstate['state']
    charinfo['statedate'] = charstate['statedate']
    charinfo['statedatetime'] = charstate['statedatetime']
    charinfo['priority'] = charstate['priority']
    charclan = getcharclan(character,date)
    charinfo['clan'] = charclan['clan']
    charinfo['bloodline'] = charclan['bloodline']
    charinfo['sect'] = charclan['sect']
    chargen = getchargen(character,date)
    charinfo['generation'] = chargen['generation']
    chartemper = getchartemper(character,int(chargen['generation']),date)
    charinfo['blood'] = chartemper['blood']
    charinfo['bloodper'] = chartemper['bloodper']
    charinfo['willpower'] = chartemper['willpower']
    charinfo['health'] = chartemper['health']
    charinfo['path'] = chartemper['path']
    charinfo['pathlevel'] = chartemper['pathlevel']
    charmagic = getcharmagic(character,date)
    charinfo['primarythaum'] = charmagic['primarythaum']
    charinfo['primarynecro'] = charmagic['primarynecro']
    charinfo['primarythaumcount'] = charmagic['primarythaumcount']
    charinfo['primarynecrocount'] = charmagic['primarynecrocount']
    charinfo['inclanlist'] = getinitialdisciplines(charclan['clan'],charclan['bloodline'])
    charsheetinfo = getcharsheetinfo(character,date)
    charinfo['hasspecializations'] = charsheetinfo['hasspecializations']
    charinfo['haselderpowers'] = charsheetinfo['haselderpowers']
    charinfo['hastechniques'] = charsheetinfo['hastechniques']
    charinfo['hasnecro'] = charsheetinfo['hasnecro']
    charinfo['hasthaum'] = charsheetinfo['hasthaum']
    return charinfo

def getcharinclanidlist(character):
    inclantraits = gettraitsbytype('In-Clan Discipline')
    charinclans = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=inclantraits)
    idlist = []
    if charinclans:
        for object in charinclans:
            idlist.append(object.trait.id)
    return idlist

def addprimarymagic(charinfo,addthaum=0,addnecro=0):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    disctype = TraitType.objects.activeonly().get(name='Discipline')
    primarymagictype = TraitType.objects.activeonly().get(name='Primary Magic')
    primarythaumtraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Thaumaturgy'))
    thaumtraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Thaumaturgy'))
    charprimarythaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarythaumtraits)
    if charprimarythaum.count() == 0:
        charthaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=thaumtraits)
        if charthaum.count()+addthaum > 0:
            thaum = charthaum.order_by('dateactive')
            thaumlist = [] 
            primarythaumname = None
            for object in thaum:
                if object.trait.name not in thaumlist:
                    thaumlist.append(object.trait.name)
                else:
                    if primarythaumname == None:
                        primarythaumname = object.trait.name
            if primarythaumname != None:
                newtrait = Trait.objects.activeonly().filter(type=primarymagictype).get(name=primarythaumname)
                addtrait(charinfo=charinfo,trait=newtrait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None)
    primarynecrotraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Necromancy'))
    necrotraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Necromancy'))
    charprimarynecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarynecrotraits)
    if charprimarynecro.count() == 0:
        charnecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=necrotraits)
        if charnecro.count()+addnecro > 0:
            necro = charnecro.order_by('dateactive')
            necrolist = [] 
            primarynecroname = None
            for object in necro:
                if object.trait.name not in necrolist:
                    necrolist.append(object.trait.name)
                else:
                    if primarynecroname == None:
                        primarynecroname = object.trait.name
            if primarynecroname != None:
                newtrait = Trait.objects.activeonly().filter(type=primarymagictype).get(name=primarynecroname)
                addtrait(charinfo=charinfo,trait=newtrait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None)
    return False

def addrituals(charinfo,addthaum=0,addnecro=0):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    disctype = TraitType.objects.activeonly().get(name='Discipline')
    primarymagictype = TraitType.objects.activeonly().get(name='Primary Magic')
    ritualtype = TraitType.objects.activeonly().get(name='Ritual')
    #Thaumaturgical Rituals
    primarythaumtraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Thaumaturgy'))
    thaumtraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Thaumaturgy'))
    charprimarythaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarythaumtraits)
    if charprimarythaum.count() == 0:
        charthaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=thaumtraits)
        if charthaum.count() > 0:
            disccount = 1
        else:
            disccount = 0
    else:
        primarythaumtrait = Trait.objects.activeonly().filter(type=disctype).filter(name=charprimarythaum.order_by('dateactive')[0].trait.name)
        charthaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarythaumtrait)
        disccount = charthaum.count()
    disccount = disccount+addthaum
    if disccount > 0:
        rituallevel = 1
        while disccount >= rituallevel:
            ritualname = ''.join(['Thaumaturgical Ritual ',unicode(rituallevel)])
            newtrait = Trait.objects.activeonly().filter(type=ritualtype).get(name=ritualname)
            charhasnewtrait = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=newtrait).count()
            if charhasnewtrait == 0:
                addtrait(charinfo=charinfo,trait=newtrait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None)
            rituallevel = rituallevel + 1
    #Necromantic Rituals
    primarynecrotraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Necromancy'))
    necrotraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Necromancy'))
    charprimarynecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarynecrotraits)
    if charprimarynecro.count() == 0:
        charnecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=necrotraits)
        if charnecro.count() > 0:
            disccount = 1
        else:
            disccount = 0
    else:
        primarynecrotrait = Trait.objects.activeonly().filter(type=disctype).filter(name=charprimarynecro.order_by('dateactive')[0].trait.name)
        charnecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarynecrotrait)
        disccount = charnecro.count()
    disccount = disccount+addnecro
    if disccount > 0:
        rituallevel = 1
        while disccount >= rituallevel:
            ritualname = ''.join(['Necromantic Ritual ',unicode(rituallevel)])
            newtrait = Trait.objects.activeonly().filter(type=ritualtype).get(name=ritualname)
            charhasnewtrait = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=newtrait).count()
            if charhasnewtrait == 0:
                addtrait(charinfo=charinfo,trait=newtrait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None)
            rituallevel = rituallevel + 1
    return True

def userviewindex(nmodel,user,nviewname=None,pkid=None):
    userinfo = getuserinfo(user)
    if nmodel.__name__ in ['Chapter']:
        model = getchapterlist(user,nviewname)
    if nmodel.__name__ in ['ChapterAddress']:
        if userinfo['isadmin'] == True:
            model = Chapter.objects.activeonly()
            if nmodel.__name__ == 'ChapterAddress':
                model = ChapterAddress.objects.activeonly()
        else:
            stafflist = Staff.objects.activeonly().filter(user=user)
            staffchapterlist = []
            for object in stafflist:
                staffchapterlist.append(object.chapter.id)
            chapterlist = Chapter.objects.activeonly().filter(pk__in=staffchapterlist)
            if nmodel.__name__ == 'ChapterAddress':
                model = ChapterAddress.objects.activeonly().filter(chapter__in=staffchapterlist)
            else:
                model = chapterlist
    elif nmodel.__name__ in ['Character']:
        model = getcharlist(user,'owned')
    elif nmodel.__name__ in ['Subscription']:
        if pkid == None:
            model = Subscription.objects.all()
        else:
            puser = User.objects.get(pk=pkid)
            model = Subscription.objects.filter(user=puser)
    else:
        model = nmodel.objects.activeonly()
    return model 

def userviewform(nform,user):
    userinfo = getuserinfo(user)
    form = nform
    if nform.__name__ == 'ChapterAddressForm':
        if userinfo['isadmin'] == True:
            chapterlist = Chapter.objects.activeonly()
        elif userinfo['isdirector'] == True:
            d = StaffType.objects.activeonly().filter(isdirector=True)
            stafflist = Staff.objects.activeonly().filter(type__in=d).filter(user=user)
            mychapters = []
            for object in stafflist:
                mychapters.append(object.chapter.id)
            chapterlist = Chapter.objects.activeonly().filter(pk__in=mychapters)
        else:
            chapterlist = Chapter.objects.none()
        form = nform(user=user)
        form.fields['chapter'].queryset = chapterlist
    return form

def isowned(nmodel, nuser):
    if not nmodel:
        return True
    if nmodel.__class__.__name__ == 'Chapter':
        directors = StaffType.objects.activeonly().filter(isdirector=True)
        staff = Staff.objects.activeonly().filter(chapter=nmodel).filter(user=nuser).filter(type__in=directors)
        if staff.count() > 0:
            return True
    if nmodel.__class__.__name__ == 'Character':
        owner = CharacterOwner.objects.activeonly().filter(character=nmodel).filter(user=nuser).filter(iscontroller=True)
        if owner.count() > 0:
            return True
    return False

def isapprover(nmodel, nuser):
    approvers = StaffType.objects.activeonly().filter(isapprover=True)
    chapteridlist = []
    if not nmodel:
        return True
    if nmodel.__class__.__name__ == 'Character':
        chapteridlist = [nmodel.chapter.id]
    if nmodel.__class__.__name__ == 'CharacterTrait':
        chapteridlist = [nmodel.character.chapter.id]
    if nmodel.__class__.__name__ == 'User':
        ownedcharacters = CharacterOwner.objects.activeonly().filter(user=user)
        for object in ownedcharacters:
            if object.id not in chapteridlist:
                chapteridlist.append(object.id)
    staff = Staff.objects.activeonly().filter(chapter__in=chapteridlist).filter(user=nuser).filter(type__in=approvers)
    if staff.count() > 0:
        return True
    return False

def ischaracterdirector(character,user):
    chapter = Chapter.objects.activeonly().filter(pk=character.chapter.id)
    directors = StaffType.objects.activeonly().filter(isdirector=True)
    directorlist = getidlist(directors)
    staff = Staff.objects.activeonly().filter(user=user).filter(chapter=chapter).filter(type__in=directors)
    if staff:
        return True
    else:
        return False

def ischaracterapprover(character,user):
    chapter = Chapter.objects.activeonly().filter(pk=character.chapter.id)
    approvers = StaffType.objects.activeonly().filter(isapprover=True)
    approverlist = getidlist(approvers)
    staff = Staff.objects.activeonly().filter(user=user).filter(chapter=chapter).filter(type__in=approvers)
    if staff:
        return True
    else:
        return False

def ischaractercontroller(character,user):
    controllers = CharacterOwner.objects.activeonly().filter(character=character).filter(user=user).filter(iscontroller=True)
    if controllers:
        return True
    else:
        return False

def isinclan(character,trait,date=None):
    charinclans = getchartraitsbytype(character,'In-Clan Discipline',date)
    if charinclans:
        for object in charinclans:
            if object.trait.name == trait.name:
                return True
    return False

def getdatetime(ndate,ntime):
    if ndate == '' and ntime == '':
        return None
    if ndate == '':
        date = ''.join([str(datetime.today().year),'-',str(datetime.today().month),'-',str(datetime.today().day)])
    else:
        date = ndate
    if ntime == '':
        time = ''.join([str(datetime.now().hour),':',str(datetime.now().minute),':',str(datetime.now().second)])
    else:
        time = ntime
    value = datetime.strptime(''.join([date,' ',time]),'%Y-%m-%d %H:%M:%S')
    return value

def getfirstowner(nform,pkid):
    if nform.Meta.model.__name__ == 'Character':
        owners = CharacterOwner.objects.activeonly().filter(character=pkid).filter(iscontroller=True).order_by('dateactive')
        if owners:
            value = UserProfile.objects.filter(user=owners[0].user)[0].name
        else:
            value = ''
    else:
        value = ''
    return value

def getcharowners(character,date=None):
    owners = CharacterOwner.objects.activeonly(date).filter(character=character).filter(iscontroller=True).order_by('dateactive')
    if owners:
        return owners
    else:
        return None

def getnotes(user,notetag='all',stdate=None,enddate=None,showall=False):
    if showall == True:
        noteowners = NoteOwner.objects.filter(user=user)
    else:
        noteowners = NoteOwner.objects.activeonly().filter(user=user)
    noteidlist = []
    for object in noteowners:
        noteidlist.append(object.note.id)
    if notetag == 'all':
        notetags = NoteTag.objects.activeonly().filter(note__in=noteidlist)
    else:
        notetags = NoteTag.objects.activeonly().filter(note__in=noteidlist).filter(tag==notetag)
    noteidlist = []
    for object in noteowners:
        noteidlist.append(object.note.id)
    q = Q(pk__in=noteidlist)
    if stdate != None:
        q = q & Q(dateactive >= stdate)
    if enddate != None:
        q = q & Q(dateactive <= enddate)
    notes = Note.objects.filter(q).order_by('-dateactive')
    return notes

def collectvocab():
    vocabulary = Vocabulary.objects.all()
    vocab = {}
    for object in vocabulary:
        vocab[object.name] = object.displayname
        pname = ''.join([object.name,'s'])
        vocab[pname] = object.displayplural
    return vocab

def getpost(post):
    valuelist = []
    for k in post:
        valuelist.append('"',join([k,':',post[k]]))
    notes = ','.join([valuelist])
    return notes

def removedependanttraits(charinfo, chartrait,d=False):
    if chartrait.dateexpiry != None:
        return False
    character = chartrait.character
    '''
    #Check Thaum
    if chartrait.trait.type.name == 'Discipline' and 'Thaumaturgy' in chartrait.trait.name:
        #Check Primary Magic
        primarythaumtrait = gettraitbyname('Primary Magic',chartrait.trait.name)
        charprimarythaum = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarythaumtrait)
        if charprimarythaum.count() > 0:
            primarythaumdisc = gettraitbyname('Discipline',primarythaumtrait.name)
            primarythaumcount = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarythaumdisc).count()
            if primarythaumcount - 1 < 2:
                removetrait(charinfo,charprimarythaum[0].id,d)
            #Check Ritual Levels
            ritualtype = TraitType.objects.activeonly().get(name='Ritual')
            thaumrituals = Trait.objects.activeonly().filter(type=ritualtype).filter(Q(name__contains='Thaumaturgical'))
            charthaumrituals = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=thaumrituals)
            if primarythaumcount > charthaumrituals.count():
                charthaumritualsremove = charthaumrituals.order_by('-dateactive')
                removetrait(charinfo,charthaumritualsremove[0].id,d)
    #Check Necro
    if chartrait.trait.type.name == 'Discipline' and 'Necromancy' in chartrait.trait.name:
        #Check Primary Magic
        primarynecrotrait = gettraitbyname('Primary Magic',chartrait.trait.name)
        charprimarynecro = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarynecrotrait)
        if charprimarynecro.count() > 0:
            primarynecrodisc = gettraitbyname('Discipline',primarynecrotrait.name)
            primarynecrocount = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=primarynecrodisc).count()
            if primarynecrocount - 1 < 2:
                removetrait(charinfo,charprimarynecro[0].id,d)
            #Check Ritual Levels
            ritualtype = TraitType.objects.activeonly().get(name='Ritual')
            necrorituals = Trait.objects.activeonly().filter(type=ritualtype).filter(Q(name__contains='Necromantic'))
            charnecrorituals = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=necrorituals)
            if primarynecrocount > charnecrorituals.count():
                charnecroritualsremove = charnecrorituals.order_by('-dateactive')
                removetrait(charinfo,charnecroritualsremove[0].id,d)
    '''
    #Check all dependant traits
    alltraits = Trait.objects.activeonly().exclude(cotraits=None)
    isdependantlist = []
    for object in alltraits:
        if chartrait.trait in object.cotraits.all():
            isdependantlist.append(object.id)
    chardependanttraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=isdependantlist)
    for object in chardependanttraits:
        removetrait(charinfo,object.id,d)
    return True

def removetrait(charinfo, pkid, d=False):
    chartrait = CharacterTrait.objects.filter(pk=pkid)
    if chartrait.count() > 0:
        model = chartrait.order_by('-dateactive')[0]
        if model.iscreation == True or d == True:
            model.delete()
            removedependanttraits(charinfo,model,d)
        else:
            model.dateexpiry = datetime.now()
            model.save()
            removedependanttraits(charinfo,model,d)
        fixcharacter(charinfo)
    return True

def removemodel(nmodel,pkid,d=False):
    model = nmodel.objects.get(pk=pkid)
    if model.__class__.__name__ == 'CharacterTrait':
        removedependanttraits(charinfo,model)
    model.dateexpiry = datetime.now()
    model.save()
    return True

def getcharacter(pkid,date=None):
    oneper = CharacterTrait.objects.activeonly(date).filter(character=pkid).filter(trait__in=Trait.objects.activeonly(date).filter(type__in=TraitType.objects.activeonly(date).filter(onepercharacter=True)))
    aggregate = CharacterTrait.objects.activeonly(date).filter(character=pkid).filter(trait__in=Trait.objects.activeonly(date).filter(type__in=TraitType.objects.activeonly(date).filter(aggregate=True)))
    other = CharacterTrait.objects.activeonly(date).filter(character=pkid).filter(trait__in=Trait.objects.activeonly(date).filter(type__in=TraitType.objects.activeonly(date).filter(onepercharacter=False).filter(aggregate=False)))
    charinfo = {}
    for object in oneper:
        charinfo[object.trait.type.name] = {'traitname':object.trait.name,'traitid':object.trait.id,'typename':object.trait.type.name,'typeid':object.trait.type.id,'chartraits':[object.id]}
    for object in aggregate:
        if object.trait.type.name in charinfo:
            if object.trait.name in charinfo[object.trait.type.name]:
                charinfo[object.trait.type.name][object.trait.name]['count'] = charinfo[object.trait.type.name][object.trait.name]['count'] + 1
                charinfo[object.trait.type.name][object.trait.name]['chartraits'].append(object.id)
            else:
                charinfo[object.trait.type.name][object.trait.name] = {'traitname':object.trait.name,'traitid':object.trait.id,'typename':object.trait.type.name,'typeid':object.trait.type.id,'count':1,'chartraits':[object.id]}
        else:
            charinfo[object.trait.type.name] = {}
            charinfo[object.trait.type.name][object.trait.name] = {'traitname':object.trait.name,'traitid':object.trait.id,'typename':object.trait.type.name,'typeid':object.trait.type.id,'count':1,'chartraits':[object.id]}
    for object in other:
        charinfo[object.trait.type.name] = {'traitname':object.trait.name,'traitid':object.trait.id,'typename':object.trait.type.name,'typeid':object.trait.type.id,'chartraits':[object.id]}
    return charinfo

def hidecharacter(user,charinfo):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    statetype = TraitType.objects.activeonly().filter(name='State')
    chartraits = CharacterTrait.objects.filter(character=character).filter(dateexpiry=None).order_by('dateactive')
    for object in chartraits:
        object.dateexpiry = datetime.now()
        object.datemodified = datetime.now()
        object.modifiedby = user
        object.save()
    character.dateexpiry = datetime.now()
    character.save()
    new_trait = Trait.objects.activeonly().filter(type=statetype).get(name='Hidden')
    addtrait(charinfo=charinfo, trait=new_trait, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
    return True

def killcharacter(user,charinfo):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    statetype = TraitType.objects.activeonly().filter(name='State')
    chartraits = CharacterTrait.objects.filter(character=character).filter(dateexpiry=None).order_by('dateactive')
    for object in chartraits:
        object.dateexpiry = datetime.now()
        object.datemodified = datetime.now()
        object.modifiedby = user
        object.save()
    character.dateexpiry = datetime.now()
    character.save()
    new_trait = Trait.objects.activeonly().filter(type=statetype).get(name='Dead')
    addtrait(charinfo=charinfo, trait=new_trait, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
    return True

def shelfcharacter(user,charinfo):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    statetype = TraitType.objects.activeonly().filter(name='State')
    chartraits = CharacterTrait.objects.filter(character=character).filter(dateexpiry=None).order_by('dateactive')
    for object in chartraits:
        object.dateexpiry = datetime.now()
        object.datemodified = datetime.now()
        object.modifiedby = user
        object.save()
    character.dateexpiry = datetime.now()
    character.save()
    new_trait = Trait.objects.activeonly().filter(type=statetype).get(name='Shelved')
    addtrait(charinfo=charinfo, trait=new_trait, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
    return True

def clearcharacter(charinfo,reset=False):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    traits = CharacterTrait.objects.filter(character=character)
    for object in traits:
        object.delete()
    if reset == True:
        new_trait = Trait.objects.activeonly().filter(type=TraitType.objects.activeonly().get(name='State')).get(name='New')
        addtrait(charinfo=charinfo, trait=new_trait, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
        secondary_trait = Trait.objects.activeonly().filter(type=TraitType.objects.activeonly().get(name='Priority')).get(name='Secondary')
        addtrait(charinfo=charinfo, trait=secondary_trait, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
        morality_trait = Trait.objects.activeonly().filter(type=TraitType.objects.activeonly().get(name='Morality')).get(name='Morality')
        addtrait(charinfo=charinfo, trait=morality_trait, iscreation=True, isfree=True, authorizedby=None, number=5)
    return True

def cleartostep(charinfo,step=0,fixed=False):
    character = charinfo['character']
    typelist = []
    steptype = TraitType.objects.activeonly().get(name='Step Complete')
    statetype = TraitType.objects.activeonly().get(name='State')
    states = Trait.objects.activeonly().filter(type=statetype)
    prioritytype = TraitType.objects.activeonly().get(name='Priority')
    priorities = Trait.objects.activeonly().filter(type=prioritytype)
    charstates = CharacterTrait.objects.filter(character=character).filter(trait__in=states)
    if charstates:
        if charstates.order_by('-dateactive')[0].trait.name != 'New':
            return False
    if step == 0:
        return False
    if step >= 1:
        steptrait = Trait.objects.activeonly().filter(type=steptype).get(name=''.join(['Step ',unicode(step)]))
        charsteptrait = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=steptrait)
        if charsteptrait:
            dateactive = charsteptrait.order_by('-dateactive')[0].dateactive
            cleartraits = CharacterTrait.objects.activeonly().filter(character=character).filter(Q(dateactive__gte=dateactive)).exclude(trait__in=states).exclude(trait__in=priorities).exclude(trait=steptrait)
            for object in cleartraits:
                object.delete()
            return True
        else:
            return False
    return False

def upgradecharacter(user, pkid):
    return True

def prioritizecharacter(user, character):
    charinfo = getcharstate(character)
    if not charinfo['state'] == 'Active':
        return -101
    mycharacters = CharacterOwner.objects.activeonly().filter(user=user).filter(iscontroller=True)
    for object in mycharacters:
        if object.character.chapter.type.id == character.chapter.type.id:
            charstate = getcharstate(object.character)
            if charstate['state'] == 'Active' and charstate['priority'] == 'Primary':
                return -102
    priorities = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=Trait.objects.activeonly().filter(type__in=TraitType.objects.activeonly().filter(name='Priority')))
    for object in priorities:
        object.dateexpiry = datetime.now()
        object.save()
    primarytrait = Trait.objects.activeonly().get(name='Primary')
    CharacterTrait(character=character, trait=primarytrait, authorizedby=None, iscreation=False, isfree=False, dateactive=datetime.now()).save()
    return 100

def finalizecharacter(user, charinfo):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    ttypes = TraitType.objects.activeonly().filter(name='State')
    states = Trait.objects.activeonly().filter(type=ttypes)
    cstates = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=states)
    for object in cstates:
        object.dateexpiry = datetime.now()
        object.save()
    pending = states.get(name='Pending');
    #Remove the Inept Discipline if applicable
    charinepts = CharacterTrait.objects.sfilter(character=character,trait='Inept',traittype='Discipline')
    if charinepts.count() > 0:
        charinept = charinepts.order_by('-dateactive')[0]
        charinept.dateexpiry = datetime.now()
        charinept.save()
    addtrait(charinfo=charinfo, trait=pending, iscreation=False, isfree=False, authorizedby=systemuser, number=1)
    return True

def getcharacterlist(user):
    characterowners = CharacterOwner.objects.activeonly().filter(user=user).filter(iscontroller=True)
    characterlist = []
    for object in characterowners:
        characterlist.append(object.character.id)
    characters = Character.objects.activeonly().filter(pk__in=characterlist)
    return characters

def getinitialdisciplines(clan, bloodline):
    disciplinelist = []
    if clan == 'Assamite':
        if bloodline == 'Vizier':
            disciplinelist = ['Auspex','Celerity','Quietus'] 
        elif bloodline == 'Sorcerer':
            disciplinelist = ['Obfuscate','Quietus','Thaumaturgy: Lure of Flame'] 
        else:
            disciplinelist = ['Celerity','Obfuscate','Quietus']
    elif clan == 'Brujah':
        if bloodline == 'True Brujah':
            disciplinelist = ['Potence','Presence','Temporis']
        else:
            disciplinelist = ['Celerity','Potence','Presence']
    elif clan == 'Setite':
        if bloodline == 'Tlacique':
            disciplinelist = ['Presence','Obfuscate','Protean']
        elif bloodline == 'Vipers':
            disciplinelist = ['Potence','Presence','Serpentis']
        else:
            disciplinelist = ['Obfuscate','Presence','Serpentis']
    elif clan == 'Gangrel':
        if bloodline == 'Coyote':
            disciplinelist = ['Celerity','Obfuscate','Protean']
        elif bloodline == 'Noiad':
            disciplinelist = ['Animalism','Auspex','Protean']
        elif bloodline == 'Ahrimane':
            disciplinelist = ['Animalism','Presence','Thaumaturgy: Path of Elemental Mastery']
        else:
            disciplinelist = ['Animalism','Fortitude','Protean']
    elif clan == 'Giovanni':
        disciplinelist = ['Dominate','Potence','Necromancy: Sepulchre Path']
    elif clan == 'Lasombra':
        if bloodline == 'Kiasyd':
            disciplinelist = ['Dominate','Mythreceria','Obtenebration']
        else:
            disciplinelist = ['Dominate','Potence','Obtenebration']
    elif clan == 'Malkavian':
        if bloodline == 'Ananke':
            disciplinelist = ['Auspex','Dementation','Presence']
        elif bloodline == 'Knight of the Moon':
            disciplinelist = ['Auspex','Dominate','Obfuscate']
        else:
            disciplinelist = ['Auspex','Dementation','Obfuscate']
    elif clan == 'Nosferatu':
        disciplinelist = ['Animalism','Obfuscate','Potence']
    elif clan == 'Toreador':
        if bloodline == 'Ishtarri':
            disciplinelist = ['Celerity','Fortitude','Presence']
        else:
            disciplinelist = ['Auspex','Celerity','Presence']
    elif clan == 'Tremere':
        if bloodline == 'Telyav':
            disciplinelist = ['Auspex','Presence','Thaumaturgy: Path of Blood']
        else:
            disciplinelist = ['Auspex','Dominate','Thaumaturgy: Path of Blood']
    elif clan == 'Tzimisce':
        if bloodline == 'Carpathian':
            disciplinelist = ['Animalism','Auspex','Dominate']
        elif bloodline == 'Koldun':
            disciplinelist = ['Animalism','Auspex','Thaumaturgy: Path of Elemental Mastery']
        else:
            disciplinelist = ['Animalism','Auspex','Vicissitude']
    elif clan == 'Ventrue':
        if bloodline == 'Crusader':
            disciplinelist = ['Auspex','Dominate','Fortitude']
        else:
            disciplinelist = ['Dominate','Fortitude','Presence']
    elif clan == 'Baali':
        if bloodline == 'Angellis Ater':
            disciplinelist = ['Daimoinon','Dominate']
        else:
            disciplinelist = ['Daimoinon','Obfuscate','Presence']
    elif clan == 'Cappadocian':
        if bloodline == 'Samedi':
            disciplinelist = ['Fortitude','Obfuscate','Thanatosis']
        elif bloodline == 'Lamia':
            disciplinelist = ['Fortitude','Necromancy: Mortis Path','Potence']
        else:
            disciplinelist = ['Auspex','Fortitude','Necromancy: Mortis Path']
    elif clan == 'Ravnos':
        if bloodline == 'Brahman':
            disciplinelist = ['Animalism','Auspex','Chimeristry']
        else:
            disciplinelist = ['Animalism','Fortitude','Chimeristry']
    elif clan == 'Salubri':
        if bloodline == 'Healer':
            disciplinelist = ['Auspex','Fortitude','Obeah']
        else:
            disciplinelist = ['Auspex','Fortitude','Valeren']
    elif clan == 'Daughter of Cacophony':
        disciplinelist = ['Fortitude','Melpominee','Presence']
    elif clan == 'Gargoyle':
        disciplinelist = ['Fortitude','Potence','Visceratika']
    return disciplinelist

def addinclans(charinfo, dateactive=datetime.now()):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    inclantype = TraitType.objects.activeonly().get(name='In-Clan Discipline')
    inclantraits = Trait.objects.activeonly().filter(type=inclantype)
    charinclans = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=inclantraits)
    if charinclans:
        for object in charinclans:
            object.dateexpiry = datetime.now()
    disciplinelist = getinitialdisciplines(charinfo['clan'],charinfo['bloodline'])
    inclantraits = Trait.objects.activeonly().filter(type=inclantype).filter(name__in=disciplinelist)
    for object in inclantraits:
        addtrait(charinfo=charinfo, trait=object, iscreation=True, isfree=True, authorizedby=systemuser, number=1, date=None, dateactive=dateactive)
    return True

def getraritycost(charinfo, trait, date=None):
    newtraitlist = getraritymerits(charinfo, trait, date)
    xpcost = trait.level
    for newtrait in newtraitlist:
        xpcost = xpcost + newtrait.level
    return xpcost

def getraritymerits(charinfo, trait, date=None):
    character = charinfo['character']
    newtraits = []
    merittype = TraitType.objects.activeonly(date).get(name='Merit')
    clan = charinfo['clan']
    bloodline = trait.name
    if bloodline not in ['Assamite','Cappadocian','Gangrel','Tremere','Tzimice','Ventrue']:
        bloodline = 'None'
    setting = charinfo['chaptertype']
    sect = charinfo['sect']
    #List of clan rarity by Clan, Bloodline, Setting, and Sect
    rarities = {
        'Assamite':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                 },
            'Vizier':{
                'Camarilla/Anarch':{'Camarilla':2,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                 },
            'Sorcerer':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                 },
            },
        'Baali':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                },
            'Angellis Ater':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                },
            },
        'Brujah':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            },
        'Caitiff':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            }, 
        'Cappadocian':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':2},
                },
            'Lamia':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':2},
                },
            'Samedi':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':2},
                },
            },
        'Daughter of Cacophony':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':4,'Sabbat':4},
                },
            },
        'Gangrel':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                },
            'Coyote':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':0},
                },
            'Noaid':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                },
            'Ahrimane':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                },
            },
        'Gargoyle':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':4,'Sabbat':4},
                },
            },
        'Giovanni':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':2,'Anarch':2,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':6},
                },
            },
        'Lasombra':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':2,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':0},
                },
            },
        'Malkavian':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            },
        'Nosferatu':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            },
        'Ravnos':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':2,'Anarch':2,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                },
            },
        'Salubri':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':4,'Sabbat':2},
                },
            },
        'Setite':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':2,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            },
        'Toreador':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':0,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':0,'Sabbat':0},
                },
            },
        'Tremere':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':4,'Sabbat':4},
                },
            'Telyav':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':4,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':4,'Sabbat':2},
                },
            },
        'Tzimisce':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':6,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':0},
                },
            'Carpathian':{
                'Camarilla/Anarch':{'Camarilla':4,'Anarch':6,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':6,'Sabbat':0},
                },
            },
        'Ventrue':{
            'None':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':2,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':2},
                },
            'Crusader':{
                'Camarilla/Anarch':{'Camarilla':0,'Anarch':2,'Sabbat':6},
                'Sabbat':{'Camarilla':6,'Anarch':2,'Sabbat':0},
                },
            },
        }
    #List of free bloodlines by Setting, Sect, and Bloodline
    frees={
        'Camarilla/Anarch':{
            'Camarilla':['Samedi','Vizier','Carpathian'],
            'Anarch':['Samedi'],
            'Sabbat':[],
            },
        'Sabbat':{
            'Camarilla':[],
            'Anarch':[],
            'Sabbat':['Telyav','Coyote','Crusader']
            },
        }
    #List of inappropriate Bloodlines by Sect and Bloodline
    inappropriates={
        'Camarilla':[],
        'Anarch':['Vizier','Sorcerer','Volgirre'],
        'Sabbat':['True Brujah','Lamia','Brahman','Healer','Volgirre','Carpathian'],
        }
    #Determine rarity from the rarity list
    rarity = 0
    if clan in rarities:
        if bloodline in rarities[clan]:
            rarity = rarities[clan][bloodline][setting][sect]
    #Find the bloodline's merit
    blmerit = None
    if trait.name in frees[setting][sect]:
        blmerit = Trait.objects.activeonly(date).filter(type=merittype).get(name=''.join(['Bloodline: ',trait.name, ' (', charinfo['sect'], ')']))
    elif trait.name not in ['None','Vestiges of Greatness']:
        blmerit = Trait.objects.activeonly(date).filter(type=merittype).get(name=''.join(['Bloodline: ',trait.name]))
    #Find the bloodline's merit's level (cost)
    blmeritlevel = 0
    if blmerit is not None:
        blmeritlevel = blmerit.level
    #Determine if this bloodline is inappropriate for its sect. Inappropriate bloodlines add a merit with a cost of 1
    inappropriate = 0
    inappropriatemerit = Trait.objects.activeonly(date).filter(type=merittype).get(name='Rarity: Inappropriate Clan')
    if trait.name in inappropriates[sect]:
        inappropriate = 1
    #If the total of rarity, bloodline cost, and the conditional extra inappropriate merit is more than 6, add only the Restricted clan merit
    if rarity + blmeritlevel + inappropriate >= 6:
        rarity = 6
        blmerit = None
        inappropriate = 0
    #Find the rarity merit based on the above logic
    raritymerit = None
    if rarity > 0:
        raritymerit = Trait.objects.activeonly(date).filter(type=merittype).filter(Q(name__contains='Rarity')).get(level=rarity)
    #If these new merits have been found, add the merits to a list and return the list
    if blmerit is not None:
        newtraits.append(blmerit)
    if trait.name == 'Vestiges of Greatness':
        newtraits.append(Trait.objects.activeonly().filter(type=merittype).get(name=trait.name))
    if raritymerit is not None:
        newtraits.append(raritymerit)
    if inappropriate > 0:
        newtraits.append(inappropriatemerit)
    return newtraits

def getchartraitinfo(character,status=None,date=None):
    basetraits = CharacterTrait.objects.showonly(date).filter(character=character)
    if status == 'pending':
        chartraits = basetraits.filter(authorizedby=None)
    elif status == 'approved':
        chartraits = basetraits.exclude(authorizedby=None)
    else:
        chartraits = basetraits
    chartraitinfo = {}
    for object in chartraits:
        label = gettraitlabel(character,ctrait=object,date=date)
        if object.trait.type.onepercharacter == True:
            key = object.trait.type.name.replace(' ','_')
        else:
            key = ''.join([object.trait.type.name.replace(' ','_'),'_',object.trait.name.replace(' ','_')])
        if key not in chartraitinfo:
            if object.authorizedby == None:
                authuser = {'username':'','id':''}
            else:
                authuser = {'username':object.authorizedby.username,'id':object.authorizedby.id}
            chartraitinfo[key] = {'name':object.trait.name,
                'label':label,
                'id':object.trait.id,
                'type':object.trait.type.name,
                'typeid':object.trait.type.id,
                'level':object.trait.level,
                'count':0,
                'iscreation':object.iscreation,
                'isfree':object.isfree,
                'authorizedby':authuser['username'],
                'authorizedbyid':authuser['id'],
            }
        chartraitinfo[key]['count'] = chartraitinfo[key]['count'] + 1
    return chartraitinfo

def getavailabletypes(user, character):
    approvertype = StaffType.objects.activeonly().filter(isapprover=True)
    directortype = StaffType.objects.activeonly().filter(isdirector=True)
    isapprover = Staff.objects.activeonly().filter(type__in=approvertype).filter(chapter=character.chapter).filter(user=user).count()
    isdirector = Staff.objects.activeonly().filter(type__in=directortype).filter(chapter=character.chapter).filter(user=user).count()
    isowner = CharacterOwner.objects.activeonly().filter(iscontroller=True).filter(character=character).filter(user=user).count()
    q = Q(name=None)
    if isowner > 0:
        q = q|Q(availtocontroller=True)
    if isapprover > 0:
        q = q|Q(availtoapprover=True)
    if isdirector > 0:
        q = q|Q(availtodirector=True)
    atypes = TraitType.objects.activeonly().filter(q).order_by('name')
    return atypes

def getavailabletraitsbytype(character, ntypename, initial=False):
    traittype = TraitType.objects.activeonly().get(name=ntypename)
    traits = Trait.objects.activeonly().filter(isadmin=False).filter(type=traittype)
    charclan = getcharclan(character)
    ctraits = CharacterTrait.objects.showonly().filter(character=character)
    excludelist = []
    #Find Merit rules related character traits
    if ntypename == 'Merit':
        merittype = TraitType.objects.activeonly().get(name='Merit')
        merits = Trait.objects.activeonly().filter(type=merittype)
        charmerits = ctraits.filter(character=character).filter(trait__in=merits)
        meritremaining = 7
        charpath = 0
        meritidlist = []
        if charmerits.count() > 0:
            for object in charmerits:
                if object.isfree == False:
                    meritremaining = meritremaining - object.trait.level
                if 'Path' in object.trait.name:
                    charpath = charpath + 1
                excludelist.append(object.trait.id) 
        traits = traits.filter(Q(level__lte=meritremaining))
    #Find Flaw rules related character traits
    elif ntypename == 'Flaw':
        flawtype = TraitType.objects.activeonly().get(name='Flaw')
        flaws = Trait.objects.activeonly().filter(type=flawtype)
        charflaws = ctraits.filter(trait__in=flaws)
        flawidlist = []
        if charflaws.count() > 0:
            for object in charflaws:
                excludelist.append(object.trait.id)
    #Find Initial Discipline rules related character traits
    elif ntypename == 'Discipline':
        charinclans = ctraits.filter(iscreation=True).filter(trait__in=Trait.objects.activeonly().filter(type=TraitType.objects.activeonly().get(name='In-Clan Discipline')))
        charinclanlist = []
        for object in charinclans:
            charinclanlist.append(object.trait.name)
        if initial == True:
            charinclanlist.append('Inept')
    #Limit the selection of Unnatural Adaptations
    elif ntypename == 'Unnatural Adaptation':
        uatype = TraitType.objects.activeonly().get(name='Unnatural Adaptation')
        uatraits = Trait.objects.activeonly().filter(type=uatype)
        charua = ctraits.filter(trait__in=uatraits)
        if charua.count() >= 2:
            traits = traits.none()
        for object in charua:
            excludelist.append(object.trait.id)
    #Limit the selection of Infernal Gifts
    elif ntypename == 'Gift':
        gifttype = TraitType.objects.activeonly().get(name='Gift')
        majorgifttraits = Trait.objects.activeonly().filter(type=gifttype).filter(level=2)
        minorgifttraits = Trait.objects.activeonly().filter(type=gifttype).filter(level=1)
        charmajorgifts = ctraits.filter(trait__in=majorgifttraits)
        charminorgifts = ctraits.filter(trait__in=mainrgifttraits)
        charmerit1 = getcharsheettraitsbyname(character,'Merit','Infernal Heritage')
        charmerit2 = getcharsheettraitsbyname(character,'Merit','Infernal Power')
        cherspecial = getcharsheettraitsbyname(character,'Special','Minor Infernal Effect')
        if charmajorgift.count() >= charmerit1.count()+charmerit2.count():
            for object in majorgifttraits:
                excludelist.append(object.id)
        if charminorgift.count() >= charspecial.count():
            for object in majorgifttraits:
                excludelist.append(object.id)
        for object in charmajorgifts:
            excludelist.append(object.trait.id)
        for object in charminorgifts:
            excludelist.append(object.trait.id)
    elif ntypename == 'Thaumaturgic Ritual':
        dabbler = ctraits.sfilter(character=character,trait='Sorcerous Dabbler',traittype='Merit')
        if dabbler.count() > 0:
            traits = traits.exclude(level__in[4,5])
            ritualtype = TraitType.objects.activeonly().get(name='Thaumaturgical Ritual')
            level1s = Trait.objects.activeonly().filter(type=ritualtype).filter(level=1)
            level2s = Trait.objects.activeonly().filter(type=ritualtype).filter(level=2)
            level3s = Trait.objects.activeonly().filter(type=ritualtype).filter(level=3)
            charlevel1s = ctraits.filter(trait__in=level1s)
            charlevel2s = ctraits.filter(trait__in=level2s)
            charlevel3s = ctraits.filter(trait__in=level3s)
            if charlevel1s.count() > 0:
                traits = traits.exclude(level__in=[2,3])
                if charlevel1s.count() >= 3:
                    traits = traits.exclude(level=1)
            if charlevel2s.count() > 0:
                traits = traits.exclude(level__in=[1,3])
                if charlevel2s.count() >= 2:
                    traits = traits.exclude(level=2)
            if charlevel3s.count() > 0:
                traits = traits.exclude(level__in=[1,2])
                if charlevel3s.count() >= 1:
                    traits = traits.exclude(level=3)
    traits = traits.exclude(pk__in=excludelist)
    #Collect limiting lists
    traitidlist = []
    for object in traits:
        include = True
        #Find ChapterTypes
        chaptertypes = object.chaptertypes.all()
        if chaptertypes.count() > 0:
            if character.chapter.type not in chaptertypes:
                include = False
        #Find CharacterTypes
        charactertypes = object.charactertypes.all()
        if charactertypes.count() > 0:
            if character.type not in charactertypes:
                include = False
        #Include Required Traits
        cotraits = object.cotraits.all()
        if cotraits.count() > 0:
            charcotraits = ctraits.filter(trait__in=cotraits)
            if charcotraits.count() == 0:
                include = False
        #Exclude Banned Traits
        bantraits = object.bantraits.all()
        if bantraits.count() > 0:
            charbantraits = ctraits.filter(trait__in=bantraits)
            if charbantraits.count() > 0:
                include = False
        #Custom Merit Rules
        if ntypename == 'Merit':
            #Golconda Seeker
            if object.name == 'Golconda Seeker':
                charmoralitytraits = getcharsheettraitsbyname(character,'Morality','Morality')
                charmorality = charmoralitytraits.count()
                charloretraits = getcharsheettraitsbyname(character,'Skill','Lore')
                charlore = charloretraits.count()
                if charmorality < 5 or charpath > 0 or charlore < 4:
                    include = False
        #Custom Character Creation rules
        if initial == True:
            #Custom In-Clan Discipline Rules
            if ntypename == 'In-Clan Discipline':
                if charclan['clan'] == 'Caitiff':
                    if charclan['bloodline'] == 'Vestiges of Greatness':
                        if object.name not in ['Animalism','Auspex','Celerity','Dementation','Dominate','Fortitude','Obfuscate','Potence','Presence','Protean','Serpentis','Quietus','Obtenebration','Vicissitude','Chimeristry']:
                            include = False
                    else:
                        if object.name not in ['Animalism','Auspex','Celerity','Dominate','Fortitude','Obfuscate','Potence','Presence']:
                            include = False
                elif charclan['bloodline'] == 'Pliable Blood':
                    if object.name not in ['Auspex','Celerity','Dementation','Dominate','Fortitude','Presence','Protean','Quietus','Serpentis']:
                        include = False
            #Custom Discipline Rules
            if ntypename == 'Discipline':
                if object.name not in charinclanlist:
                    include = False
        else:
            if object.name == 'Inept':
                include = False
        #If everything is alright, include this trait
        if include == True:
            traitidlist.append(object.id)
    return traits.filter(pk__in=traitidlist).order_by('name')

def getavailabletraits(character, traittypename=None, initial=False):
    charinfo = getcharclan(character)
    merittotal = calcmerit(character)
    meritremaining = 7 - int(merittotal)
    e = Q(type=None)
    #Build Available trait list
    q = Q(chaptertypes=None)|Q(chaptertypes__in=[character.chapter.type.id])
    q = q & (Q(charactertypes=None)|Q(charactertypes__in=[character.type.id]))
    q = q & (Q(isadmin=False))
    if traittypename != None:
        traittype = TraitType.objects.activeonly().get(name=traittypename)
        if traittype.onepercharacter == True:
            charcount = getchartraittypecount(character,traittypename)
            if charcount > 0:
               return Trait.objects.none()
        q = q & (Q(type=traittype))
    #Exclude traits that have bans
    traits = Trait.objects.activeonly().exclude(bantraits=None)
    bantraitlist = []
    for object in traits:
        bantraits = object.bantraits.all()
        charbantraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=bantraits)
        if charbantraits.count() > 0:
            bantraitlist.append(object.id)
    e = e | (Q(pk__in=bantraitlist))
    #Custom Merit Rules
    if traittypename == 'Merit':
        e = e | (Q(level__gt=meritremaining))
        merittype = TraitType.objects.activeonly().get(name='Merit')
        merits = gettraitsbytype('Merit')
        morality = gettraitbyname('Morality','Morality')
        paths = Trait.objects.activeonly().filter(trait__in=merits).filter(Q(name__contains='Path'))
        charmoralitycount = CharacterTrait.objects.showonly().filter(character=character).filter(trait=morality).count()
        charpathcount = CharacterTrait.objects.showonly().filter(character=character).filter(trait__in=paths).count()
        #Golconda Seeker
        if charmoralitycount < 5 or charpathcount > 0:
            e = e | (Q(type=merittype)&Q(name='Golconda Seeker'))
    #Post Clan Selection Rules
    if charinfo['clan']:
        traits = Trait.objects.activeonly().exclude(cotraits=None)
        traitlist = []
        for object in traits:
            cotraits = Trait.objects.activeonly().filter(pk=object.id).values('cotraits')
            chartraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=cotraits)
            if chartraits.count() > 0:
                traitlist.append(object.id)
        q = q & (Q(cotraits=None)|Q(pk__in=traitlist))
        if initial == True:
            inclantype = TraitType.objects.activeonly().get(name='In-Clan Discipline')
            disciplinelist = []
            if charinfo['clan'] == 'Caitiff':
                if charinfo['bloodline'] == 'Vestiges of Greatness':
                    disciplinelist = ['Animalism','Auspex','Celerity','Dementation','Dominate','Fortitude','Obfuscate','Potence','Presence','Protean','Serpentis','Quietus','Obtenebration','Vicissitude','Chimeristry']
                else:
                    disciplinelist = ['Animalism','Auspex','Celerity','Dominate','Fortitude','Obfuscate','Potence','Presence']
            elif charinfo['bloodline'] == 'Pliable Blood':
                disciplinelist = ['Auspex','Celerity','Dementation','Dominate','Fortitude','Presence','Protean','Quietus','Serpentis']
            if disciplinelist:
                disciplines = Trait.objects.activeonly().filter(type=inclantype).filter(name__in=disciplinelist)
                disciplineids = getidlist(disciplines)
                e = e | (Q(type=inclantype)&~Q(pk__in=disciplineids))
            disciplinetype = TraitType.objects.activeonly().filter(name='Discipline')
            inclantraits = gettraitsbytype('In-Clan Discipline')
            inclans = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=inclantraits)
            inclannamelist = []
            if inclans:
                for object in inclans:
                    inclannamelist.append(object.trait.name)
            e = e | (Q(type=disciplinetype)&~Q(name__in=inclannamelist))
    atraits = Trait.objects.activeonly().filter(q).exclude(e).distinct().order_by('name')
    return atraits

def getatraittype(character, traittype, initial=False):
    clans = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=Trait.objects.activeonly().filter(name='Clan')).order_by('-dateactive')
    chaptertypeid = character.chapter.type.id
    charactertypeid = character.type.id
    alltraits = Trait.objects.activeonly().filter(Q(chaptertypes=None)|Q(chaptertypes__in=[chaptertypeid])).filter(Q(charactertypes=None)|Q(charactertypes__in=[charactertypeid])).filter(Q(isadmin=False)).filter(type=traittype)
    clanname = ''
    clanid = 0
    if clans:
        clanname = clans[0].name
        clanid = clans[0].id
        if initial == True:
            disciplines = getinitialdisciplines(charinfo['clan'],charinfo['bloodline'])
            disc = TraitType.objects.activeonly().filter(name='Discipline')
            atraits = alltraits.filter(Q(cotraits=None)|(Q(cotraits__in=[clanid]))).exclude(Q(type=disc)&~Q(pk__in=disciplines))
        else:
            atraits = alltraits.filter(Q(cotraits=None)|(Q(cotraits__in=[clanid])))
    else:
        atraits = alltraits
    return atraits

def getsheettraits(character,date=None):
    chartraits = CharacterTrait.objects.showonly(date).filter(character=character).exclude(authorizedby=None).order_by('dateactive')
    return chartraits

def getcreationtraits(character, date=None):
    chartraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(iscreation=True).order_by('dateactive')
    return chartraits

def getpendingtraits(character, date=None):
    newstate = gettraitbyname('State','New',date)
    isnew = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=newstate).count()
    userlist = []
    if isnew > 0:
        systemuser = User.objects.get(username='system')
        userlist = [systemuser]
    chartraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(iscreation=False).filter(Q(authorizedby=None)|Q(authorizedby__in=userlist)).order_by('dateactive')
    return chartraits

def getlogtraits(character, date=None):
    chartraits = CharacterTrait.objects.filter(character=character).order_by('-dateactive')
    return chartraits

def getsubscriptionenddate(user):
    subscription = Subscription.objects.activeonly().filter(user=user).order_by('-dateexpiry')
    dateexpiry = datetime.now()
    if subscription:
        if subscription[0].dateexpiry != None:
            dateexpiry = subscription[0].dateexpiry
        elif datetime.now() < datetime(2014,02,01,0,0,0):
            dateexpiry = datetime(2014,2,1,0,0,0)
    return dateexpiry + timedelta(days=365)

def gettypexpcost(character,traittype,date=None):
    generationtrait = gettraitbyname('Background','Generation',date)
    generation = getchartraitcount(character,generationtrait,date)
    perlevelcost = 0
    if generation in [1,0]:
        perlevelcost = traittype.xpcost1
    if generation == 2:
        perlevelcost = traittype.xpcost2
    if generation == 3:
        perlevelcost = traittype.xpcost3
    if generation == 4:
        perlevelcost = traittype.xpcost4
    if generation == 5:
        perlevelcost = traittype.xpcost5
    return perlevelcost

def getxpcost(character,trait,date=None):
    charclan = getcharclan(character)
    generationtrait = gettraitbyname('Background','Generation',date)
    generation = getchartraitcount(character,generationtrait,date)
    isoutofclan = 0
    if trait.type.name == 'Discipline':
        inclans = getchartraitsbytype(character,'In-Clan Discipline')
        if inclans:
            isoutofclan = 1
            for object in inclans:
                if object.trait.name == trait.name:
                    isoutofclan = 0
    curlevel = 1
    if trait.type.multiplyxp == True:
        curlevel = trait.level
        if not date:
            date = datetime.now()
        tcount = 0
        q = Q(character=character)&Q(trait=trait)
        if trait.dateactive != None:
            q = q & Q(dateactive__lt=trait.dateactive)
        ttraits = CharacterTrait.objects.activeonly(date).filter(q)
        if ttraits:
            tcount = ttraits.count() + 1
        curlevel = curlevel * tcount
    perlevelcost = 0
    if generation in [1,0]:
        perlevelcost = trait.type.xpcost1 + isoutofclan
    if generation == 2:
        perlevelcost = trait.type.xpcost2 + isoutofclan
    if generation == 3:
        perlevelcost = trait.type.xpcost3 + isoutofclan
    if generation == 4:
        perlevelcost = trait.type.xpcost4 + isoutofclan
    if generation >= 5:
        perlevelcost = trait.type.xpcost5 + (isoutofclan * 2)
    xpcost = perlevelcost * curlevel
    return xpcost

def getchartraitxpcost(chartrait,generation,isoutofclan,tcount):
    trait = chartrait.trait
    date = chartrait.dateactive
    if not date:
        date = datetime.now()
    xpcost = gettraitxpcost(trait=trait,generation=generation,isoutofclan=isoutofclan,tcount=tcount,fcount=0,date=date)
    return xpcost

def gettraitxpcost(trait,generation,isoutofclan=0,tcount=0,fcount=0,date=None):
    curlevel = 1
    if trait.type.multiplyxp == True:
        curlevel = trait.level
        if trait.type.aggregate == True:
            curlevel = curlevel * tcount
    perlevelcost = 0
    if generation in [1,0]:
        perlevelcost = trait.type.xpcost1 + isoutofclan
    elif generation == 2:
        perlevelcost = trait.type.xpcost2 + isoutofclan
    elif generation == 3:
        perlevelcost = trait.type.xpcost3 + isoutofclan
    elif generation == 4:
        perlevelcost = trait.type.xpcost4 + isoutofclan
    else:
        perlevelcost = trait.type.xpcost5 + (isoutofclan * 2)
    if trait.type.name == 'Flaw' and trait.level > 7 - fcount:
        xpcost = 0
    else:
        xpcost = perlevelcost * curlevel
    return xpcost

def getfloorxp(ndate=None):
    if ndate == None:
        ndate = today()
    xdate = date(2014,3,1)
    floorxp = 0
    while True:
        if xdate < ndate:
            floorxp = floorxp + 3.33333333333
        else:
            break
        xyear = int(xdate.year)
        xmonth = int(xdate.month) + 1
        if xmonth == 13:
            xyear = xyear + 1
            xmonth = 1
        xdate = date(xyear,xmonth,1)
    return floor(floorxp)

def calcpaths(character, nritualtype, date=None):
    disciplinetype = TraitType.objects.activeonly(date).get(name='Discipline')
    paths = Trait.objects.activeonly(date).filter(type=disciplinetype).filter(Q(name__contains=nritualtype))
    charpaths = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=paths)
    pathtotal = charpaths.count()
    return pathtotal

def calcritual(character, nritualtype, date=None):
    if nritualtype == 'Thaumaturgy':
        ritualtype = TraitType.objects.activeonly(date).get(name='Thaumaturgical Ritual')
    elif nritualtype == 'Necromancy':
        ritualtype = TraitType.objects.activeonly(date).get(name='Necromantic Ritual')
    rituals = Trait.objects.activeonly(date).filter(type=ritualtype)
    ritualtotal = rituals.count()
    return ritualstotal

def calcmerit(character, date=None):
    merits = gettraitsbytype('Merit',date)
    charmerits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=merits)
    merittotal = 0
    for object in charmerits:
        merittotal = merittotal + object.trait.level
    return merittotal

def calcXP(character, date=None):
    if date == None:
        date = datetime.now()
    #Collect data into model objects
    ctraits = CharacterTrait.objects.filter(character=character)
    ttypes = TraitType.objects.activeonly(date).filter(name__in=['State','Priority','Flaw','Background'])
    traits = Trait.objects.activeonly(date).filter(type__in=ttypes)
    statetraits = traits.filter(type=ttypes.get(name='State'))
    prioritytraits = traits.filter(type=ttypes.get(name='Priority'))
    flaws = traits.filter(type=ttypes.get(name='Flaw'))
    backgrounds = traits.filter(type=ttypes.get(name='Background'))
    attended = Attendance.objects.activeonly(date).filter(character=character).exclude(authorizedby=None).filter(rejectedby=None).order_by('-dateactive')
    #Find the date the character became Primary, if any
    cprimarytraits = ctraits.filter(trait=prioritytraits.filter(name='Primary'))
    primarydate = None
    if cprimarytraits.count() > 0:
        primarydate = cprimarytraits.order_by('-dateactive')[0].dateactive.date()
    #Find floor XP and apply it. Characters start with 30+floor
    xpfloor = 0
    if primarydate:
        xpfloor = getfloorxp(primarydate)
    xptotal = 30 + xpfloor
    #Loop through every attended game and add a maximum of 10 XP per month to the total
    months = {}
    for object in attended:
        #Collect date information about the Attended Event
        month = object.event.dateheld.month
        monthstring = ''.join(['00',str(month)])[-2:]
        year = object.event.dateheld.year
        monthname = ''.join([str(year),monthstring])
        if monthname not in months:
            mrange = monthrange(year,month)
            months[monthname] = {'name':monthname,'year':year,'month':month,'ldom':mrange[1], 'xpawarded':0}
        #Find the character's state and priority at the time of the game
        cstates = ctraits.filter(Q(dateactive=None)|Q(dateactive__lte=object.event.dateheld)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=object.event.dateheld)).filter(trait__in=statetraits)
        cstate = ''
        if cstates:
            cstate = cstates.order_by('-dateactive')[0].trait.name
        cpriorities = ctraits.filter(Q(dateactive=None)|Q(dateactive__lte=object.event.dateheld)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=object.event.dateheld)).filter(trait__in=prioritytraits)
        cpriority = ''
        if cpriorities:
            cpriority = cpriorities.order_by('-dateactive')[0].trait.name
        #Award XP if appropriate
        xpawarded = 0
        if cstate == 'Active':
            if cpriority == 'Primary':
                xpawarded = object.xpawarded
        if months[monthname]['xpawarded'] + xpawarded <= 10:
            months[monthname]['xpawarded'] = months[monthname]['xpawarded'] + xpawarded
        else:
            months[monthname]['xpawarded'] = 10
    #Add up all XP
    for item in months:
        xptotal = xptotal + months[item]['xpawarded']
    generation = int(getchargen(character,date)['generation'])
    #Calculate XP Cost
    cpaytraits = ctraits.filter(isfree=False)
    xpspent = 0
    for object in cpaytraits:
        isoutofclan = 0
        if object.trait.type.name == 'Discipline':
            istraitinclan = isinclan(character,object.trait,object.dateactive)
            if not istraitinclan:
                isoutofclan = 1
        tcount = 0
        if object.trait.type.aggregate == True:
            tcount = CharacterTrait.objects.activeonly(object.dateactive).filter(character=character).filter(trait=object.trait).count()
        xpcost = gettraitxpcost(trait=object.trait,generation=generation,isoutofclan=isoutofclan,tcount=tcount,fcount=0,date=object.dateactive)
	# Undo for Flaws
	if object.trait.type.name == 'Flaw':
	    # These are calculated below
	    # TODO: Add a filter for this above instead of doing it at the end like this
	    xpcost = 0
        xpspent = xpspent + xpcost
    #Add XP for up to 7 points worth of flaws
    cflaws = ctraits.filter(Q(dateactive=None)|Q(dateactive__lte=date)).filter(Q(dateexpiry=None)|Q(dateexpiry__gte=date)).filter(isfree=False).filter(trait__in=flaws)
    xpgain = 0
    for object in cflaws:
        xpcost = gettraitxpcost(trait=object.trait,generation=0,isoutofclan=0,tcount=0,fcount=0,date=object.dateactive)
        xpgain = xpgain + xpcost
    if xpgain < -7:
        xpgain = -7
    xpspent = xpspent + xpgain
    xpvalues = {'xptotal':floor(xptotal),'xpspent':floor(xpspent)}
    return xpvalues

def addnoteowner(note,user):
    noteowners = NoteOwner.objects.activeonly().filter(note=note).filter(user=user)
    if not noteowners:
        NoteOwner(note=note,user=user,dateactive=datetime.now()).save()
    return True

def addnote(author,subject,body,characterlist=[],chapterlist=[],traitlist=[],traitlevel=None,stafftype=None):
    model = Note(author=author,subject=subject,body=body,dateactive=datetime.now())
    model.save()
    words=model.body.split()
    for word in words:
        if word[0]=='#':
            tag = word.replace('#','')
            NoteTag(note=model,tag=tag, dateactive=datetime.now()).save()
    for item in characterlist:
        character = Character.objects.activeonly().get(pk=item)
        owners = CharacterOwner.objects.activeonly().filter(character=character)
        for object in owners:
            addnoteowner(note=model,user=object.user)
    for item in chapterlist:
        chapter = Chapter.objects.activeonly().get(pk=item)
        characters = Character.objects.activeonly().filter(chapter=chapter)
        for object in characters:
            owners = CharacterOwner.objects.activeonly().filter(character=character)
            for object2 in owners:
                if stafftype:
                    staff = Staff.objects.activeonly().filter(chapter=chapter).filter(user=object2)
                    if staff:
                        addnoteowner(note=model,user=object2.user)
                else:
                    addnoteowner(note=model,user=object2.user)
    for item in traitlist:
        trait = Trait.objects.activeonly().get(pk=item)
        chartraits = CharacterTrait.objects.activeonly().filter(trait=trait)
        chartraitdict = {}
        for object in chartraits:
            value = object.character.id
            if value not in chartraidict:
                chartraitdict[value] = 0
            chartraitdict[value] = chartraitdict[value] + object.trait.level
        for value in chartraitdict:
            if chartraitdict[value] == traitlevel or traitlevel == None:
                character = Character.objects.activeonly().get(pk=value)
                owners = CharacterOwner.objects.activeonly().filter(character=character)
                for object in owners:
                    addnoteowner(note=model,user=object)
    return True     

def rejectcharacter(character,user,rejectionnote):
    statetype = TraitType.objects.activeonly().get(name='State')
    statetraits = Trait.objects.activeonly().filter(type=statetype)
    charpendingtraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=statetraits)
    for object in charpendingtraits:
        object.dateexpiry = datetime.now()
    newtrait = Trait.objects.activeonly().filter(type=statetype).get(name='New')
    CharacterTrait(character=character,trait=newtrait,authorizedby=user,modifiedby=user,datecreated=datetime.now(),dateactive=datetime.now()).save()
    addnote(author=user,subject='Character Rejected',body=rejectionnote,characterlist=[character.id])
    return True

def approvecharacter(character,user):
    statetype = TraitType.objects.activeonly().get(name='State')
    states = Trait.objects.activeonly().filter(type=statetype)
    cstates = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=states)
    for object in cstates:
        object.dateexpiry = datetime.now()
        object.save()
    activetrait = Trait.objects.activeonly().filter(type=statetype).get(name='Active')
    CharacterTrait(character=character,trait=activetrait,authorizedby=user,modifiedby=user,dateactive=datetime.now()).save()
    ctraits = CharacterTrait.objects.activeonly().filter(character=character).filter(authorizedby=None)
    for object in ctraits:
        object.authorizedby = user
        object.modifiedby = user
        object.dateauthorized = datetime.now()
        object.datemodified = datetime.now()
        object.save()
    return True

def addattendance(user,character,event,xpawarded=5,authorizedby=None):
    cur = Attendance.objects.activeonly().filter(event=event).filter(Q(user=user)|Q(character=character))
    if cur:
        return False
    else:
        Attendance(user=user,character=character,event=event,xpawarded=xpawarded,ishidden=False,authorizedby=authorizedby,rejectedby=None,dateactive=datetime.now()).save()

def addtrait(charinfo,trait,iscreation=False,isfree=False,authorizedby=None,number=1,calculateonly=False,tryonly=False,date=None,dateactive=None):
    character = charinfo['character']
    systemuser = User.objects.get(username='system')
    if dateactive == None:
        dateactive = datetime.now()
    avail = {'available':True,'xpcost':0}
    newtraitlist = []
    if iscreation == True:
        isfree = True
    #Auspicious Rules
    if trait.type.name == 'Auspicious':
        merittype = TraitType.objects.activeonly().get(name='Merit')
        auspicious = Trait.objects.activeonly().filter(type=merittype).get(name='Auspicious')
        causpicious = CharacterTrait.objects.showonly().filter(character=character).filter(trait=auspicious)
        if causpicious.count() == 0:
            newtraitlist.append(auspicious)
    #Background Rules
    elif trait.type.name == 'Background':
        backgroundtype = TraitType.objects.activeonly(date).get(name='Background')
        currenttraits = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=trait)
        if currenttraits.count() >= 5:
            return False
        if charinfo['clan'] == 'Caitiff' and charinfo['state'] == 'New' and trait.name == 'Generation' and currenttraits.count() >= 2:
            return False
        if trait.name == 'Generation':
            if charinfo['state'] == 'New':
                if currenttraits:
                    dateactive = currenttraits.order_by('-dateactive')[0].dateactive + timedelta(0,1)
        elif trait.name == 'Influence: The Elite':
            specialtype = TraitType.objects.activeonly(date).get(name='Special')
            newtraitlist.append(Trait.objects.activeonly(date).filter(type=specialtype).get(name='Influence: The Elite Specialization'))
            hasmerit = CharacterTrait.objects.sfilter(character=character, trait='Monopoly', traittype='Merit',showonly=True,date=date)
            if hasmerit.count() > 0:
                newtraitlist.append(newtraitlist[0])
        elif trait.name == 'Influence: The Underworld':
            specialtype = TraitType.objects.activeonly(date).get(name='Special')
            newtraitlist.append(Trait.objects.activeonly(date).filter(type=specialtype).get(name='Influence: The Underworld Specialization'))
            hasmerit = CharacterTrait.objects.sfilter(character=character, trait='Monopoly', traittype='Merit',showonly=True,date=date)
            if hasmerit.count() > 0:
                newtraitlist.append(newtraitlist[0])
    #Bloodline Rules
    elif trait.type.name == 'Bloodline':
        newtraitlist = getraritymerits(charinfo, trait)
    #Discipline Rules
    elif trait.type.name == 'Discipline':
        if 'Thaumaturgy' in trait.name or 'Necromancy' in trait.name:
            addthaum = 0
            addnecro = 0
            if 'Thaumaturgy' in trait.name:
                addthaum = 1
            elif 'Necromancy' in trait.name:
                addnecro = 1
            if tryonly == False:
                disciplineok = addtrait(charinfo=charinfo,trait=trait,iscreation=False,isfree=False,authorizedby=None,tryonly=True)
                if disciplineok == True:
                    addprimarymagic(charinfo,addthaum,addnecro)
                    addrituals(charinfo,addthaum,addnecro)
    #Flaw Rules
    elif trait.type.name == 'Flaw':
        charflaws = None
        charflaws = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=trait)
        if charflaws:
            return False
    #Merit Rules
    elif trait.type.name == 'Merit':
        charmeritcount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=trait).count()
        if charmeritcount > 0:
            return False
        merittotal = calcmerit(character,date)
        if merittotal + trait.level > 7:
            return False
        if calculateonly == True:
            return trait.level
        if trait.name in ['Loremaster','Natural Linguist']:
            specialtype = TraitType.objects.activeonly(date).get(name='Special')
            if trait.name == 'Loremaster':
                skillname = 'Lore'
                specialtyname = 'Lore Specialization'
            elif trait.name == 'Natural Linguist':
                skillname = 'Linguistics'
                specialtyname = 'Linguistics Specialization'
            newspecialty = Trait.objects.activeonly(date).filter(type=specialtype).get(name=specialtyname)
            charskills = CharacterTrait.objects.sfilter(character=character,trait=skillname,traittype='Skill',showonly=True,date=date).count()
            charspecialties = CharacterTrait.objects.sfilter(character=character,trait=specialtyname,traittype='Special',showonly=True,date=date).count()
            while True:
                if charspecialties >= charskills * 2:
                    break
                else:
                    newtraitlist.append(newspecialty)
                    charspecialties = charspecialties + 1
        elif trait.name == 'Monopoly':
            specialtype = TraitType.objects.activeonly(date).get(name='Special')
            newelitespecialty = Trait.objects.activeonly(date).filter(type=specialtype).get(name='Influence: The Elite Specialization')
            newunderworldspecialty = Trait.objects.activeonly(date).filter(type=specialtype).get(name='Influence: The Underworld Specialization')
            charelites = CharacterTrait.objects.sfilter(character=character,trait='Influence: The Elite',traittype='Background',showonly=True,date=date).count()
            charelitespecialties = CharacterTrait.objects.sfilter(character=character,trait='Influence: The Elite Specialization',traittype='Special',showonly=True,date=date).count()
            charunderworlds = CharacterTrait.objects.sfilter(character=character,trait='Influence: The Underworld',traittype='Background',showonly=True,date=date).count()
            charunderworldspecialties = CharacterTrait.objects.sfilter(character=character,trait='Influence: The Underworld Specialization',traittype='Special',showonly=True,date=date).count()
            while True:
                if charelitespecialties >= charelites * 2:
                    break
                else:
                    newtraitlist.append(newelitespecialty)
                    charelitespecialties = charelitespecialties + 1
            while True:
                if charunderworldspecialties >= charunderworlds * 2:
                    break
                else:
                    newtraitlist.append(newunderworldspecialty)
                    charunderworldspecialties = charunderworldspecialties + 1
        elif trait.name == 'Blood of the Tzimice':
            skilltype = TraitType.activeonly().get(name='Skill')
            lore = Trait.objects.activeonly().filter(type=skilltype).get(name='Lore')
            newtraitlist = [lore,lore]
            charlore = CharacterTrait.objects.sfilter(character=character,trait='Lore',traittype='Skill').filter(isfree=False)
            if charlore.count() > 0:
                charlore1 = charlore.order_by('dateactive')[0]
                charlore1.isfree = True
                charlore1.save()
                newtraitlist[1] = None
            if charlore.count() > 1:
                charlore2 = charlore.order_by('dateactive')[1]
                charlore2.isfree = True
                charlore2.save()
                newtraitlist[0] = None
    #Path Rules
    elif trait.type.name == 'Path':
        merittype = TraitType.objects.activeonly(date).get(name='Merit')
        clanpath = Trait.objects.activeonly(date).filter(type=merittype).filter(name__contains=trait.name).filter(name__contains=''.join(['(',charinfo['clan'],')']))
        sectpath = Trait.objects.activeonly(date).filter(type=merittype).filter(name__contains=trait.name).filter(name__contains=''.join(['(',charinfo['sect'],')']))
        if clanpath:
            newmeritname = ''.join([trait.name,' (',charinfo['clan'],')'])
        elif sectpath:
            newmeritname = ''.join([trait.name,' (',charinfo['sect'],')'])
        else:
            infernalheritage = Trait.objects.activeonly(date).filter(type=merittype).get(name='Infernal Heritage')
            charinfernalheritage = CharacterTrait.objects.showonly(date).filter(character=character).filter(trait=infernalheritage)
            if charinfernalheritage.count() > 0:
                newmeritname = ''.join([trait.name,' (Infernal Heritage)'])
            else:
                newmeritname = trait.name
        newmerit = Trait.objects.activeonly(date).filter(type=merittype).get(name=newmeritname)
        if calculateonly == True:
            return newmerit.level
        else:
            newok = addtrait(charinfo=charinfo,trait=newmerit,iscreation=False,isfree=False,authorizedby=authorizedby,tryonly=True,date=date)
            if newok == True:
                newtraitlist.append(newmerit)
            else:
                return False
    #Ritual Rules
    elif trait.type.name in ['Thaumaturgical Ritual','Necromantic Ritual']:
        ritualtypename = trait.type.name
        magictype = None
        magickey = None
        if trait.type.name == 'Thaumaturgical Ritual':
            magictype = 'Thaumaturgy'
            magickey = 'primarythaum'
        elif trait.type.name == 'Necromantic Ritual':
            magictype = 'Necromancy'
            magickey = 'primarythaum'
        #Find Primary Path Level
        charmagic = getcharmagic(character,date)
        disctype = TraitType.objects.activeonly(date).get(name='Discipline')
        disccount = 0
        if charmagic[magickey] == '':
            magicdisc = Trait.objects.activeonly(date).filter(type=disctype).filter(Q(name__contains=magictype))
            charmagicdisc = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=magicdisc)
            if charmagicdisc:
                disccount = 1
        else:
            disccount = charmagic[''.join([magickey,'count'])]
        #Find Ritual Level and cancel if over maximum
        magicdisc = Trait.objects.activeonly(date).filter(type=disctype).filter(Q(name__contains=magictype))
        charritecount = getchartraittypecount(character,trait.type.name,date)
        charmagiccount = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait__in=magicdisc).count()
        if charritecount + 1 > charmagiccount:
            return False
    #Skill Rules
    elif trait.type.name == 'Skill':
        specialtype = TraitType.objects.activeonly(date).get(name='Special')
        if trait.name == 'Lore':
            newtraitlist.append(Trait.objects.activeonly(date).filter(type=specialtype).get(name='Lore Specialization'))
            hasmerit = CharacterTrait.objects.sfilter(character=character, trait='Loremaster', traittype='Merit',showonly=True,date=date)
            if hasmerit.count() > 0:
                newtraitlist.append(newtraitlist[0])
        elif trait.name == 'Linguistics':
            newtraitlist.append(Trait.objects.activeonly(date).filter(type=specialtype).get(name='Linguistics Specialization'))
            hasmerit = CharacterTrait.objects.sfilter(character=character, trait='Natural Linguist', traittype='Merit',showonly=True,date=date)
            if hasmerit.count() > 0:
                newtraitlist.append(newtraitlist[0])
    #Step Complete Rules
    elif trait.type.name == 'Step Complete':
        if authorizedby == None:
            authorizedby = systemuser
        if trait.name == 'Step 7':
            #Handle the Inept Flaw
            charisinept = CharacterTrait.objects.sfilter(character=character,trait='Inept',traittype='Discipline')
            if charisinept.count() > 0:
		step7traittype = TraitType.objects.activeonly().get(name='Discipline')
                disciplines = Trait.objects.activeonly().filter(type=step7traittype)
                chardisciplines = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=disciplines)
                chardisciplinelist = []
                for chardiscipline in chardisciplines:
                    if chardiscipline.trait.name not in chardisciplinelist:
                        chardisciplinelist.append(chardiscipline.trait.name)
                inclantype = TraitType.objects.activeonly().get(name='In-Clan Discipline')
                inclans = Trait.objects.activeonly().filter(type=inclantype)
                charinclans = inclans.filter(name__in=chardisciplinelist)
                charineptinclans = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=inclans).exclude(trait__in=charinclans)
                if charineptinclans.count() > 0:
                    charineptinclan = charineptinclans.order_by('-dateactive')[0]
                    charineptinclan.dateexpiry = datetime.now()
                    charineptinclan.save()
    #State Rules
    elif trait.type.name == 'State':
        if authorizedby == None:
            authorizedby = systemuser
    # Calculate XP
    xpcost = 0
    if isfree == False:
        curcount = getchartraitcount(character,trait,date)
        xpcost = gettraitxpcost(trait=trait,generation=int(charinfo['generation']),isoutofclan=0,tcount=curcount+1,fcount=0,date=None)
        for newtrait in newtraitlist:
            xpcost = xpcost + gettraitxpcost(trait=newtrait,generation=int(charinfo['generation']),isoutofclan=0,tcount=0,fcount=0,date=None)
        if xpcost > float(charinfo['xpremaining']):
            return False
    # This is as far as calulations need to go
    if calculateonly == True:
        return xpcost
    # This is as far as tries need to go
    if tryonly == True:
        return True
    #This will add the given trait. If the input number is greater than one, it will call the function again until the character has that number of traits or the function fails. It will also add any related traits at this time
    CharacterTrait(character=character, trait=trait, iscreation=iscreation, isfree=isfree, authorizedby=authorizedby, datecreated=datetime.now(), dateactive=dateactive).save()
    for newtrait in newtraitlist:
        addtrait(charinfo=charinfo,trait=newtrait,iscreation=False,isfree=False,authorizedby=systemuser,date=date)
    #If there are traits in addtraits, it will add them as free traits
    addtraits = trait.addtraits.all()
    for object in addtraits:
        charaddtraits = CharacterTrait.objects.showonly().filter(character=character).filter(trait=object)
        if charaddtraits.count() == 0:
            addtrait(charinfo=charinfo, trait=object, iscreation=False, isfree=True, authorizedby=systemuser, date=date)
    #If number is greater than 1, this will add traits until it reaches the number requested
    traitcount = 1
    while True:
        if traitcount < number:
            traitcount = traitcount + 1
            canadd = addtrait(charinfo=charinfo, trait=trait, iscreation=iscreation, isfree=isfree, authorizedby=authorizedby, tryonly=True, date=date)
            if canadd == True:
                addtrait(charinfo=charinfo, trait=trait, iscreation=iscreation, isfree=isfree, authorizedby=authorizedby, number=1, tryonly=False, date=date)
            else:
                break
        else:
            break
    #if trait.type.name == 'Bloodline':
    #    charinfo['bloodline'] = trait.name
    #    addinclans(charinfo)
    if trait.type.name == 'Path':
        moralitytype = TraitType.objects.activeonly(date).get(name='Morality')
        moralitytrait = Trait.objects.activeonly(date).filter(type=moralitytype).get(name='Morality')
        while True:
            charmorality = CharacterTrait.objects.activeonly(date).filter(character=character).filter(trait=moralitytrait)
            if charmorality.count() > 4:
                model = charmorality.order_by('-dateactive')[0]
                model.dateexpiry = datetime.now()
                model.save()
            else:
                break
    return True

def fixstep(charinfo,stepname,typelist,count,modellist,addsec=1):
    character=charinfo['character']
    steptype = modellist['steptype']
    systemuser = modellist['systemuser']
    steptraittypes = TraitType.objects.activeonly().filter(name__in=typelist)
    steptraits = Trait.objects.activeonly().filter(type__in=steptraittypes)
    stepchartraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=steptraits)
    if stepchartraits.count() >= count:
        newtrait = Trait.objects.activeonly().filter(type=steptype).get(name=stepname)
        traitexists = CharacterTrait.objects.filter(character=character).filter(trait=newtrait)
        if traitexists.count() > 0:
            for object in traitexists:
                object.delete()
            traitexists = CharacterTrait.objects.filter(character=character).filter(trait=newtrait)
        if traitexists.count() == 0:
            dateactive = None
            i=0
            for object in stepchartraits.order_by('dateactive'):
                if i==count-1:
                    dateactive = object.dateactive + timedelta(seconds=addsec)
                i=i+1
            if dateactive == None:
                dateactive = datetime.now()
            CharacterTrait(character=character,trait=newtrait,dateactive=dateactive,authorizedby=systemuser).save()

def fixcharacter(charinfo):
    character = charinfo['character']
    #Fix system approved traits
    chartraits = CharacterTrait.objects.activeonly().filter(character=character).filter(authorizedby=None)
    systemuser = User.objects.get(username='system')
    for object in chartraits:
        if (object.trait.type.name == 'Merit' and ('Path' in object.trait.name or 'Rarity' in object.trait.name or 'Bloodline' in object.trait.name)) or object.trait.type.name in ['Primary Magic','Ritual'] or (object.iscreation == True and object.trait.type.name == 'In-Clan Discipline'):
            object.authorizedby = systemuser
            object.dateauthorized = datetime.now()
            object.save()
    #fix State
    statetype = TraitType.objects.activeonly().get(name='State')
    states = Trait.objects.activeonly().filter(type=statetype)
    allstates = CharacterTrait.objects.filter(character=character).filter(trait__in=states)
    if allstates.count() > 0:
        object = allstates.order_by('-dateactive')[0]
        object.dateexpiry = None
        object.save()
    else:
        newtrait = Trait.objects.activeonly().filter(type=statetype).get(name='New')
        dateactive = CharacterTrait.objects.filter(character=character).exclude(dateactive=None).order_by('dateactive')[0].dateactive - timedelta(seconds=1)
        CharacterTrait(character=character,trait=newtrait,dateactive=dateactive).save()
    #Fix Steps
    steptype = TraitType.objects.activeonly().get(name='Step Complete')
    modellist = {'steptype':steptype,'systemuser':systemuser}
    fixstep(charinfo=charinfo,stepname='Step 1',typelist=['Sect','Archetype'],count=2,modellist=modellist)
    fixstep(charinfo=charinfo,stepname='Step 2',typelist=['Clan','Bloodline'],count=2,modellist=modellist)
    fixstep(charinfo=charinfo,stepname='Step 3',typelist=['Clan','Bloodline'],count=2,modellist=modellist,addsec=2)
    fixstep(charinfo=charinfo,stepname='Step 4',typelist=['Attribute','Mental Focus','Physical Focus','Social Focus'],count=18,modellist=modellist)
    fixstep(charinfo=charinfo,stepname='Step 5',typelist=['Skill','Archetype'],count=20,modellist=modellist)
    fixstep(charinfo=charinfo,stepname='Step 6',typelist=['Background'],count=6,modellist=modellist)
    fixstep(charinfo=charinfo,stepname='Step 7',typelist=['Discipline'],count=4,modellist=modellist)
    #Fix Morality
    step1complete = Trait.objects.activeonly().filter(type=steptype).get(name='Step 1')
    charstep1complete = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=step1complete)
    if charstep1complete.count() > 0:
        datecomplete = charstep1complete.order_by('dateactive')[0].dateactive
        moralitytype = TraitType.objects.activeonly().get(name='Morality') 
        moralitytrait = Trait.objects.activeonly().filter(type=moralitytype).get(name='Morality') 
        charmorality = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=moralitytrait).filter(Q(dateactive__lte=datecomplete))
        if charmorality.count() > 0:
            for object in charmorality:
                object.iscreation = True
                object.isfree = True
                if object.authorizedby == systemuser:
                    object.authorizedby = None
                    object.authroizeddate = None
                object.save()
        
    #Fix creation traits
    step7trait = Trait.objects.activeonly().filter(type=steptype).get(name='Step 7')
    charstep7 = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=step7trait)
    if charstep7.count() > 0:
        dateactive = charstep7.order_by('-dateactive')[0].dateactive
        creationlist = ['Morality','Sect','Archetype','Clan','Bloodline','Physical Focus','Mental Focus','Social Focus','In-Clan Discipline','Skill','Attribute','Background','Discipline']
        creationtypes = TraitType.objects.activeonly().filter(name__in=creationlist)
        rightcreationtraits = Trait.objects.activeonly().filter(type__in=creationtypes)
        wrongcreationtraits = Trait.objects.activeonly().exclude(type__in=creationtypes)
        charrighttraits = CharacterTrait.objects.filter(character=character).filter(trait__in=rightcreationtraits).filter(Q(dateactive__lte=dateactive))
        charwrongtraits = CharacterTrait.objects.filter(character=character).filter(trait__in=wrongcreationtraits)
        if charrighttraits.count() > 0:
            for object in charrighttraits:
                object.iscreation = True
                object.isfree = True 
                object.modifiedby = systemuser
                object.modifieddate = datetime.now()
                object.save()
        if charwrongtraits.count() > 0:
            for object in charwrongtraits:
                object.iscreation = False
                object.modifiedby = systemuser
                object.modifieddate = datetime.now()
                object.save()
    #Mark Creation Traits as Free
    creationtraits = CharacterTrait.objects.filter(character=character).filter(iscreation=True)
    for object in creationtraits:
        object.isfree = True
        object.save()
    #Fix Backgrounds
    backgroundtype = TraitType.objects.activeonly().get(name='Background')
    backgroundtraits = Trait.objects.activeonly().filter(type=backgroundtype)
    for object in backgroundtraits:
        while True:
            chartraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=object)
            if chartraits.count() > 5:
                thistrait = chartraits.order_by('-dateactive')[0]
                thistrait.dateexpiry = datetime.now()
                thistrait.modifieddate = datetime.now()
                thistrait.modifiedby = systemuser
                thistrait.save()
            else:
                break
    #Fix Primary Magic
    disctype = TraitType.objects.activeonly().get(name='Discipline')
    primarymagictype = TraitType.objects.activeonly().get(name='Primary Magic')
    primarythaumtraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Thaumaturgy'))
    primarynecrotraits = Trait.objects.activeonly().filter(type=primarymagictype).filter(Q(name__contains='Necromancy'))
    #Fix Primary Thaum
    while True:
        charprimarythaumtraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarythaumtraits)
        if charprimarythaumtraits.count() > 1:
            thistrait = charprimarythaumtraits.order_by_('-dateactive')[0]
            thistrait.dateexpiry = datetime.now()
            thistrait.modifiedby = systemuser
            thistrait.save()
        else:
            break
    if charprimarythaumtraits.count() == 1:
        thaumdiscname = charprimarythaumtraits[0].trait.name
        thaumdisc = Trait.objects.activeonly().filter(type=disctype).get(name=thaumdiscname)
        charthaumdisc = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=thaumdisc)
        if charthaumdisc.count() < 2:
            for object in charprimarythaumtraits.order_by('-dateactive'):
                object.dateexpiry = datetime.now()
                object.modifiedby = systemuser
                object.save()
            charprimarythaumtraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarythaumtraits)
    if charprimarythaumtraits == 0:
        allthaumtraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Thaumaturgy'))
        charallthaumtraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=allthaumtraits)
        if charallthaumtraits.count() > 0:
            charallthaumidlist = []
            for object in charallthaumtraits.order_by('dateactive'):
                if object.trait.id not in charallthaumidlist:
                    charallthaumidlist.append(object.trait.id)
                else:
                    dateactive = object.dateactive
                    addtrait(charinfo=charinfo,trait=object.trait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None,dateactive=dateactive)
                    break
    #Fix Primary Necro
    while True:
        charprimarynecrotraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarynecrotraits)
        if charprimarynecrotraits.count() > 1:
            thistrait = charprimarynecrotraits.order_by_('-dateactive')[0]
            thistrait.dateexpiry = datetime.now()
            thistrait.modifiedby = systemuser
            thistrait.save()
        else:
            break
    if charprimarynecrotraits.count() == 1:
        necrodiscname = charprimarynecrotraits[0].trait.name
        necrodisc = Trait.objects.activeonly().filter(type=disctype).get(name=necrodiscname)
        charnecrodisc = CharacterTrait.objects.activeonly().filter(character=character).filter(trait=necrodisc)
        if charnecrodisc.count() < 2:
            for object in charprimarynecrotraits:
                object.dateexpiry = datetime.now()
                object.modifiedby = systemuser
                object.save()
            charprimarynecrotraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=primarynecrotraits)
    if charprimarynecrotraits == 0:
        allnecrotraits = Trait.objects.activeonly().filter(type=disctype).filter(Q(name__contains='Necromancy'))
        charallnecrotraits = CharacterTrait.objects.activeonly().filter(character=character).filter(trait__in=allnecrotraits)
        if charallnecrotraits.count() > 0:
            charallnecroidlist = []
            for object in charallnecrotraits.order_by('dateactive'):
                if object.trait.id not in charallnecroidlist:
                    charallnecroidlist.append(object.trait.id)
                else:
                    dateactive = object.dateactive
                    addtrait(charinfo=charinfo,trait=object.trait,iscreation=False,isfree=False,authorizedby=systemuser,calculateonly=False,tryonly=False,date=None,dateactive=dateactive)
                    break
    return True 

def fixall():
    characters = Character.objects.all()
    for object in characters:
        charinfo = getcharinfo(object,datetime.now())
        fixcharacter(charinfo)
    return True

def backdatecharacter(character, datediff):
    ctraits = CharacterTrait.objects.filter(character=character)
    backdate = timedelta(days=datediff)
    for ctrait in ctraits:
        ctrait.datemodified = datetime.now()
        if ctrait.dateactive is not None:
            ctrait.dateactive = ctrait.dateactive - backdate
        if ctrait.dateexpiry is not None:
            ctrait.dateexpiry = ctrait.dateexpiry - backdate
        if ctrait.dateremoved is not None:
            ctrait.dateremoved = ctrait.dateremoved - backdate
        ctrait.save()
    if character.dateactive is not None:
        character.dateactive = character.dateactive - backdate
    if character.dateexpiry is not None:
        character.dateexpiry = character.dateexpiry - backdate
    return True
