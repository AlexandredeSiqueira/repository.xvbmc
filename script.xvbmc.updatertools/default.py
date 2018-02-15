#!/usr/bin/python
#-*- coding: utf-8 -*-
import re,base64,urllib,urllib2,sys,xbmcvfs
import xbmc,xbmcaddon,xbmcgui,xbmcplugin
import os,shutil,time
import sqlite3
import utils
from resources.lib import addon_able
from resources.lib import downloader,extract
from resources.lib import common as Common
from resources.lib.common import platform,subtitleNope,nonlinux,nonelecNL
from resources.lib.common import base,basewiz,repos
from resources.lib.common import EminenceTxt,EminenceUrl,NoxSpinTxt,NoxSpinUrl,PortableTxt,PortableUrl,RPiTxt,RPiUrl,ZeitgeistTxt,ZeitgeistUrl
from resources.lib.common import EminenceTxtBld,EminenceUrlBld,NoxSpinTxtBld,NoxSpinUrlBld,PortableTxtBld,PortableUrlBld,RPiTxtBld,RPiUrlBld,ZeitgeistTxtBld,ZeitgeistUrlBld
from resources.lib import huisvrouw as nursemaid
from resources.lib import rpioc as overclck
from resources.lib import rpidev as rpidevc
ADDON=utils.ADDON
ADDON_ID=xbmcaddon.Addon().getAddonInfo('id')
AddonID='script.xvbmc.updatertools'
AddonTitle='XvBMC Nederland'
addonPath=os.path.join(os.path.join(xbmc.translatePath('special://home'),'addons'),'script.xvbmc.updatertools')
ART=xbmc.translatePath(os.path.join('special://home/addons/'+AddonID+'/resources/media/'))
artwork=base64.b64decode('c2tpbi5hZW9uLm5veC5zcGlu')
FANART=xbmc.translatePath(os.path.join('special://home/addons/'+AddonID,'fanart.jpg'))
FANARTsub=xbmc.translatePath(os.path.join('special://home/addons/'+AddonID+'/resources/media/','art.jpg'))
ICON=xbmc.translatePath(os.path.join('special://home/addons/'+AddonID,'icon.png'))
MainTitle="XvBMC Nederland"
mediaPath=os.path.join(addonPath,'resources/media')
U=ADDON.getSetting('User')
USER_AGENT='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
About='[COLOR dimgray][B]X[/B]v[B]BMC[/B] disclaimer & usage policy[/COLOR]'
Terug='[COLOR dimgray]<<<back[/COLOR]'
dialog=xbmcgui.Dialog()
dp=xbmcgui.DialogProgress()
BASEURL="https://bit.ly/XvBMC-Pi"
buildinfotxt='[COLOR gray][B] - [/B]your XvBMC build: [I]unknown[/I] [/COLOR]'
xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: [I]unknown[/I] [/COLOR]'
xvbmcUnknown='[COLOR orange]unknown build status; force update?[/COLOR] [COLOR red][B](continue at your own risk)[/B][/COLOR]'
xbmcver=xbmc.getInfoLabel("System.BuildVersion")[:4]
EXCLUDES=[ADDON_ID,'skin.estuary','plugin.program.xvbmcinstaller.nl','repository.xvbmc']
HOME=xbmc.translatePath('special://home/')
skin=xbmc.getSkinDir()
USERDATA=xbmc.translatePath(os.path.join('special://home/userdata',''))
USERADDONDATA=xbmc.translatePath(os.path.join('special://home/userdata/addon_data',''))
xxxCheck=xbmc.translatePath(os.path.join(USERADDONDATA,'plugin.program.super.favourites','Super Favourites','xXx','favourites.xml'))
xxxIcon=base64.b64decode('aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1h2Qk1DL3JlcG9zaXRvcnkueHZibWMvbWFzdGVyL3ppcHMvdHJpcGxlLXgvYWR1bHQucG5n')
def resolveUrl_settings():
 import resolveurl
 resolveurl.display_settings()
def Urlresolver_settings():
 import urlresolver
 urlresolver.display_settings()
def mainMenu():
 update,updateversie=utils.checkUpdate()
 if update=="EminenceUpdate":
  updatetxt="[COLOR orange]XvBMC update available[B]: %s[/B][/COLOR]"%(updateversie)+'[COLOR orange] (Eminence)[/COLOR]'
  Link=base64.b64decode(basewiz)+'eminence-sp.zip'
  addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
 elif update=="NoxSpinUpdate":
  updatetxt="[COLOR orange]XvBMC update available[B]: %s[/B][/COLOR]"%(updateversie)+'[COLOR orange] (NoxSpin)[/COLOR]'
  Link=base64.b64decode(basewiz)+'noxspin-sp.zip'
  addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
 elif update=="PortableUpdate":
  updatetxt="[COLOR orange]XvBMC update available[B]: %s[/B][/COLOR]"%(updateversie)+'[COLOR orange] (Portable)[/COLOR]'
  Link=base64.b64decode(base)+'update/service/portable-sp.zip'
  addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
 elif update=="RPiUpdate":
  updatetxt="[COLOR orange]XvBMC RPi-update available[B]: %s[/B][/COLOR]"%(updateversie)+'[COLOR orange] (RPi)[/COLOR]'
  forceRPi=base64.b64decode(base)+'update/service/'
  addDir('%s'%updatetxt,forceRPi,100,ART+'xvbmc.png',FANART,'')
 elif update=="ZeitgeistUpdate":
  updatetxt="[COLOR orange]XvBMC update available[B]: %s[/B][/COLOR]"%(updateversie)+'[COLOR orange] (Zeitgeist)[/COLOR]'
  Link=base64.b64decode(basewiz)+'zeitgeist-sp.zip'
  addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
 elif update=="notinstalled":
  if xbmc.getCondVisibility('System.HasAddon("service.openelec.settings")')+xbmc.getCondVisibility('System.HasAddon("service.libreelec.settings")'):
   updatetxt="[COLOR orange]unknown [COLOR red]RPi[/COLOR] version; force update[B]?[/B][/COLOR] [COLOR lime] (continue?)[/COLOR]"
   forceRPi=base64.b64decode(base)+'update/service/'
   addDir('%s'%updatetxt,forceRPi,100,ART+'xvbmc.png',FANART,'')
  elif xbmc.getCondVisibility('System.HasAddon(skin.aeon.nox.spin)'):
   if os.path.isfile(NoxSpinTxtBld):
    updatetxt="[COLOR orange]Sorry (NoxSpin) wizard status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(basewiz)+'noxspin-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   elif os.path.isfile(PortableTxtBld):
    updatetxt="[COLOR orange][B]Old[/B] (NoxSpin) portable status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(base)+'update/service/portable-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   elif os.path.isfile(Common.bldversietxt):
    updatetxt="[COLOR orange][B]Old[/B] (NoxSpin) portable status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(base)+'update/service/portable-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   elif os.path.isfile(Common.bldversietxtwiz):
    updatetxt="[COLOR orange][B]Old[/B] (NoxSpin) wizard status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(basewiz)+'noxspin-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   else:
    forceLink=base64.b64decode(basewiz)+'noxspin-sp.zip'
    addDir('%s'%xvbmcUnknown,forceLink,1,ART+'xvbmc.png',FANART,'')
  elif xbmc.getCondVisibility('System.HasAddon(skin.eminence.2)'):
   if os.path.isfile(EminenceTxtBld):
    updatetxt="[COLOR orange]Sorry (Eminence) status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(basewiz)+'eminence-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   else:
    forceLink=base64.b64decode(basewiz)+'eminence-sp.zip'
    addDir('%s'%xvbmcUnknown,forceLink,1,ART+'xvbmc.png',FANART,'')
  elif xbmc.getCondVisibility('System.HasAddon(skin.aczg)'):
   if os.path.isfile(ZeitgeistTxtBld):
    updatetxt="[COLOR orange]Sorry (Zeitgeist) status [COLOR red]unknown[/COLOR], continue anyway[B]?[/B][/COLOR]"
    Link=base64.b64decode(basewiz)+'zeitgeist-sp.zip'
    addDir('%s'%updatetxt,Link,1,ART+'xvbmc.png',FANART,'')
   else:
    forceLink=base64.b64decode(basewiz)+'zeitgeist-sp.zip'
    addDir('%s'%xvbmcUnknown,forceLink,1,ART+'xvbmc.png',FANART,'')
  else:
   updatetxt="[COLOR orange]Sorry, [COLOR red][B]unknown[/B][/COLOR] build/servicepack/update status [B] :[/B]\'-([/COLOR]"
   addItem('%s'%updatetxt,BASEURL,4,ART+'xvbmc.png')
 elif update=="noupdaterpi":
  if xbmc.getCondVisibility('System.HasAddon("service.openelec.settings")')+xbmc.getCondVisibility('System.HasAddon("service.libreelec.settings")'):
   updatetxt="[COLOR orange]You have the [B]latest[/B] [COLOR red]XvBMC[/COLOR] [COLOR lime][B]RPi[/B][/COLOR] forced updates [B] 3:[/B]-)[/COLOR]"
   addItem('%s'%updatetxt,BASEURL,4,ART+'xvbmc.png')
  else:
   updatetxt="[COLOR orange]You [B]somehow[/B] have the latest [COLOR lime]XvBMC[/COLOR] [COLOR red][B]RPi[/B][/COLOR] forced updates [B]???[/B][/COLOR]"
   addItem('%s'%updatetxt,BASEURL,4,ART+'xvbmc.png')
 else:
  updatetxt="[COLOR orange]You have the [B]latest[/B] XvBMC updates [B] :[/B]-)[/COLOR]"
  addItem('%s'%updatetxt,BASEURL,4,ART+'xvbmc.png')
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addDir('[COLOR red]XvBMC Tools[/COLOR]',BASEURL,10,ART+'tools.png',os.path.join(mediaPath,"gereedschap.jpg"),'')
 addDir('[COLOR white]XvBMC Maintenance[/COLOR]',BASEURL,20,ART+'maint.png',os.path.join(mediaPath,"onderhoud.jpg"),'')
 addDir('[COLOR dodgerblue]XvBMC About/info[/COLOR]',BASEURL,2,ART+'wtf.png',os.path.join(mediaPath,"over.jpg"),'')
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem('[COLOR gray]system information (kodi %s):[/COLOR]'%xbmcver,BASEURL,16,ART+'xvbmc.png')
 global xvbmcSPcheck
 currentOnly,xvbmcVersie=utils.checkUpdate(onlycurrent=True)
 if xvbmcVersie=="EminenceUpdate":
  try:EminenceOnline=utils.getHtml2(EminenceUrl)
  except:EminenceOnline='unknown'
  xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: %s [/COLOR]'%(currentOnly+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%EminenceOnline)
 elif xvbmcVersie=="NoxSpinUpdate":
  try:NoxSpinOnline=utils.getHtml2(NoxSpinUrl)
  except:NoxSpinOnline='unknown'
  xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: %s [/COLOR]'%(currentOnly+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%NoxSpinOnline)
 elif xvbmcVersie=="PortableUpdate":
  try:PortableOnline=utils.getHtml2(PortableUrl)
  except:PortableOnline='unknown'
  xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: %s [/COLOR]'%(currentOnly+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%PortableOnline)
 elif xvbmcVersie=="RPiUpdate":
  try:RPiOnline=utils.getHtml2(RPiUrl)
  except:RPiOnline='unknown'
  xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: %s [/COLOR]'%(currentOnly+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%RPiOnline)
 elif xvbmcVersie=="ZeitgeistUpdate":
  try:ZeitgeistOnline=utils.getHtml2(ZeitgeistUrl)
  except:ZeitgeistOnline='unknown'
  xvbmcSPcheck='[COLOR gray][B] - [/B]your service pack: %s [/COLOR]'%(currentOnly+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%ZeitgeistOnline)
 addItem('%s'%xvbmcSPcheck,BASEURL,'',os.path.join(mediaPath,"wtf.png"))
 global buildinfotxt
 buildinfo,buildversie=Common.checkXvbmcVersie()
 if buildinfo=="EminenceTxtBld":
  try:bldversion=utils.getHtml2(EminenceUrlBld)
  except:bldversion='unknown'
  buildinfotxt='[COLOR gray][B] - [/B]your system build: %s [/COLOR]'%(buildversie+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%bldversion)
 elif buildinfo=="NoxSpinTxtBld":
  try:bldversion=utils.getHtml2(NoxSpinUrlBld)
  except:bldversion='unknown'
  buildinfotxt='[COLOR gray][B] - [/B]your wizard build: %s [/COLOR]'%(buildversie+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%bldversion)
 elif buildinfo=="PortableTxtBld":
  try:bldversion=utils.getHtml2(PortableUrlBld)
  except:bldversion='unknown'
  buildinfotxt='[COLOR gray][B] - [/B]your wizard build: %s [/COLOR]'%(buildversie+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%bldversion)
 elif buildinfo=="RPiTxtBld":
  try:bldversion=utils.getHtml2(RPiUrlBld)
  except:bldversion='unknown'
  buildinfotxt='[COLOR gray][B] - [/B]your wizard build: %s [/COLOR]'%(buildversie+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%bldversion)
 elif buildinfo=="ZeitgeistTxtBld":
  try:bldversion=utils.getHtml2(ZeitgeistUrlBld)
  except:bldversion='unknown'
  buildinfotxt='[COLOR gray][B] - [/B]your wizard build: %s [/COLOR]'%(buildversie+' [COLOR dimgray][I](online: %s)[/I][/COLOR]'%bldversion)
 addItem('%s'%buildinfotxt,BASEURL,'',os.path.join(mediaPath,"wtf.png"))
 if xbmc.getCondVisibility('System.HasAddon("service.openelec.settings")')+xbmc.getCondVisibility('System.HasAddon("service.libreelec.settings")'):
  addItem('',BASEURL,'',ART+'xvbmc.png')
  addDir('[COLOR orange]XvBMC Raspberry Pi [B] -[/B] Tools, DEV. & Maintenance[/COLOR]',BASEURL,30,ART+'RPi.png',FANARTsub,'')
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem(Terug,BASEURL,3,os.path.join(mediaPath,"xvbmc.png"))
 Common.setView('movies','EPiC')
def XvBMCmaint():
 addItem('[B]C[/B]lear cache',BASEURL,22,os.path.join(mediaPath,"maint.png"))
 addItem('[B]D[/B]elete thumbnails',BASEURL,23,os.path.join(mediaPath,"maint.png"))
 addItem('[B]F[/B]ull clean [COLOR dimgray](cache, crashlogs, packages & thumbnails)[/COLOR]',BASEURL,25,os.path.join(mediaPath,"maint.png"))
 addItem('[B]P[/B]urge packages',BASEURL,26,os.path.join(mediaPath,"maint.png"))
 addItem('[B]R[/B]efresh addons[COLOR white]+[/COLOR]repos',BASEURL,27,os.path.join(mediaPath,"maint.png"))
 if int(utils.kodiver)<=16.7:
  addItem('[B][COLOR lime]X[/COLOR][/B]vBMC\'s remove addons.db',BASEURL,28,os.path.join(mediaPath,"xvbmc.png"))
 elif int(utils.kodiver)>16.7:
  addItem('[B][COLOR lime]X[/COLOR][/B]vBMC\'s enable all add-ons [COLOR dimgray](Kodi 17+ Krypton)[/COLOR]',BASEURL,29,os.path.join(mediaPath,"xvbmc.png"))
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem(About,BASEURL,2,os.path.join(mediaPath,"wtf.png"))
 addItem(Terug,BASEURL,3,os.path.join(mediaPath,"xvbmc.png"))
 Common.setView('movies','EPiC')
def XvBMCtools1():
 addItem('[B]C[/B]onvert physical paths (\'home\') to \'special\'',BASEURL,11,os.path.join(mediaPath,"maint.png"))
 addItem('[B]E[/B]nable Kodi Addons [COLOR dimgray](Kodi 17+ Krypton; [COLOR white]most[/COLOR] add-ons)[/COLOR]',BASEURL,12,os.path.join(mediaPath,"maint.png"))
 addItem('[B]E[/B]nable Kodi Addons [COLOR dimgray](Kodi 17+ Krypton; [COLOR white]all[/COLOR] add-ons)[/COLOR]',BASEURL,13,os.path.join(mediaPath,"maint.png"))
 addItem('[B]E[/B]nable Kodi Live Streams [COLOR dimgray](17+ Krypton; [COLOR white]RTMP[/COLOR])[/COLOR]',BASEURL,14,os.path.join(mediaPath,"maint.png"))
 addItem('[B]F[/B]orce close Kodi  [COLOR dimgray](Kill Kodi)[/COLOR]',BASEURL,15,os.path.join(mediaPath,"maint.png"))
 addItem('[B]L[/B]og viewer [COLOR dimgray](show \'kodi.log\')[/COLOR]',BASEURL,17,os.path.join(mediaPath,"maint.png"))
 addItem('[B]R[/B]esolveURL  -> settings',BASEURL,8,os.path.join(mediaPath,"maint.png"))
 addItem('[B]U[/B]RLResolver -> settings',BASEURL,18,os.path.join(mediaPath,"maint.png"))
 addItem('[B][COLOR lime]X[/COLOR][/B]vBMC\'s Advancedsettings unlocker [COLOR dimgray](reset)[/COLOR]',BASEURL,19,os.path.join(mediaPath,"xvbmc.png"))
 addDir('[B][COLOR lime]X[/COLOR][/B]vBMC\'s [COLOR white][B]H[/B]idden [B]g[/B]ems[B] & [/B][B]M[/B]ore [B]t[/B]ools[/COLOR] [COLOR dimgray](TiP[B]!![/B])[/COLOR]',BASEURL,40,ART+'xvbmc.png',os.path.join(mediaPath,"gereedschap.jpg"),'')
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem(About,BASEURL,2,os.path.join(mediaPath,"wtf.png"))
 addItem(Terug,BASEURL,3,os.path.join(mediaPath,"xvbmc.png"))
 Common.setView('movies','EPiC')
def XvBMCrpi():
 addItem('[COLOR white][B]R[/B][/COLOR]aspberry [COLOR white]Pi[/COLOR] extreme crapcleaner [COLOR dimgray]([B]no[/B] factory reset)[/COLOR]',BASEURL,31,os.path.join(mediaPath,"tools.png"))
 addItem('[COLOR white][B]R[/B][/COLOR]aspberry [COLOR white]Pi[/COLOR] overclock [COLOR dimgray](raspberry Pi ***only***)[/COLOR]',BASEURL,32,os.path.join(mediaPath,"overclock.png"))
 addItem('[COLOR white][B]R[/B][/COLOR]aspberry [COLOR white]Pi[/COLOR] #dev# corner [COLOR dimgray](firmware, OS, etc.)[/COLOR]',BASEURL,33,os.path.join(mediaPath,"firmware.png"))
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem(About,BASEURL,2,os.path.join(mediaPath,"wtf.png"))
 addItem(Terug,BASEURL,3,os.path.join(mediaPath,"xvbmc.png"))
 Common.setView('movies','EPiC')
def XvBMCtools2():
 addItem('[B]K[/B]odi Quick Reset [COLOR dimgray](\"rejuvenate\" XvBMC-NL build)[/COLOR]',BASEURL,41,os.path.join(mediaPath,"maint.png"))
 addItem('[B]K[/B]odi Factory Reset [COLOR dimgray](complete Kodi Krypton wipe)[/COLOR]',BASEURL,42,os.path.join(mediaPath,"maint.png"))
 addItem('[B]K[/B]odi Fresh Start [COLOR dimgray](wipe for older Kodi\'s)[/COLOR]',BASEURL,43,os.path.join(mediaPath,"maint.png"))
 addItem('[B]P[/B]ush Fixes [COLOR dimgray](for XvBMC builds)[/COLOR]',BASEURL,44,os.path.join(mediaPath,"maint.png"))
 addItem('[B]P[/B]ush XvBMC REPOsitory [COLOR dimgray](install or fix repo)[/COLOR]',BASEURL,45,os.path.join(mediaPath,"maint.png"))
 if os.path.isfile(xxxCheck):
  if xbmc.getCondVisibility('System.HasAddon("plugin.program.super.favourites")'):
   addItem('',BASEURL,'',ART+'xvbmc.png')
   addItem('[COLOR hotpink]activated: [/COLOR][COLOR pink]XvBMC\'s [B] [COLOR hotpink]x[COLOR deeppink]X[/COLOR]x[/COLOR] [/B] section ([COLOR hotpink]18[/COLOR][COLOR deeppink][B]+[/B][/COLOR])[/COLOR]',BASEURL,69,xxxIcon)
  else:
   addItem('',BASEURL,'',ART+'xvbmc.png')
   addItem('[COLOR red]\'Super Favourites\' is missing, [COLOR lime][I]click here [/I][/COLOR] to (re-)install & enable [B]18+[/B][/COLOR]',BASEURL,70,xxxIcon)
 else:
  addItem('[B]P[/B]ush x[B]X[/B]x [COLOR dimgray](\"dirty\"-up your box with some 69 and mo\')[/COLOR]',BASEURL,46,xxxIcon)
 addItem('',BASEURL,'',ART+'xvbmc.png')
 addItem(About,BASEURL,2,os.path.join(mediaPath,"wtf.png"))
 addItem(Terug,BASEURL,3,os.path.join(mediaPath,"xvbmc.png"))
 Common.setView('movies','EPiC')
def wizard(name,url):
 path=xbmc.translatePath(os.path.join('special://home/addons','packages'))
 if not os.path.exists(path):
  os.makedirs(path)
 lib=os.path.join(path,'default.zip')
 try:
  os.remove(lib)
 except:
  pass
 downloader.download(url,lib)
 if os.path.exists(lib):
  addonfolder=xbmc.translatePath(os.path.join('special://','home'))
  time.sleep(2)
  dp.create(MainTitle,'XvBMC-NL: pull update VoOdOo...','','Please Wait')
  dp.update(0,"","***Extract ZIP - Please Wait")
  Common.log("==========================================================")
  Common.log(addonfolder)
  Common.log("==========================================================")
  extract.all(lib,addonfolder,dp)
  dp.close()
  try:os.remove(lib)
  except:pass
 if int(utils.kodiver)<=16.7:
  dialog.ok(MainTitle+" : Update [COLOR green][B]finished[/B][/COLOR]",'[COLOR orange][B]!!!  HINT  !!![/B][/COLOR]','[B]Reboot[/B] Kodi to complete...','[B]Herstart[/B] Kodi ter afronding')
  Common.forceRefresh(melding=False)
 elif int(utils.kodiver)>16.7:
  utils.enableAddons(melding=False)
  time.sleep(0.5)
  choice=xbmcgui.Dialog().yesno(MainTitle+"[COLOR green][B] - success[/B][/COLOR]",' ','[B]IF[/B] add-ons do NOT work, you need to [B]reboot 1st[/B].','(een REBOOT van uw systeem is VEELAL wenselijk)',yeslabel='[COLOR lime]Reboot[/COLOR]',nolabel='[COLOR red]Continue[/COLOR]')
  if choice==1:
   time.sleep(1)
   Common.killKodi()
  elif choice==0:
   if int(utils.kodiver)>16.7:
    utils.enableAddons(melding=False)
    time.sleep(0.5)
    dialog.ok(MainTitle+" : [COLOR red]add-ons[/COLOR] [COLOR green][B]enabled[/B][/COLOR]",'[COLOR orange][B]!!!  TIP  !!![/B][/COLOR]','[B]Reboot[/B] Kodi to complete...','[B]Herstart[/B] Kodi ter afronding')
    xbmc.executebuiltin('ReloadSkin()')
 xbmc.executebuiltin("Container.Refresh")
 xbmc.sleep(5000)
def fileexchange(url,name,locatie):
 dp.create(MainTitle,'XvBMC-NL: RPi update VoOdOo...','','Please Wait')
 if not os.path.exists(locatie):os.makedirs(locatie)
 lib=os.path.join(locatie,name)
 dp.update(0,'','.file.VoOdOo.')
 try:os.remove(lib)
 except:pass
 downloader.download(url+name,lib)
 time.sleep(1)
 dp.close()
 xbmc.executebuiltin("Container.Refresh")
 xbmc.sleep(1000)
def customwizard(name,url,storeLoc,unzipLoc):
 if not os.path.exists(storeLoc):os.makedirs(storeLoc)
 lib=os.path.join(storeLoc,name)
 try:os.remove(lib)
 except:pass
 downloader.download(url+name,lib)
 if os.path.exists(lib):
  time.sleep(2)
  dp.create(MainTitle,'XvBMC-NL: just doing our VoOdOo...','','Please Wait')
  dp.update(0,'','***Mo\' XvBMC magic...')
  Common.log(str('UNWiZ@'+unzipLoc))
  extract.all(lib,unzipLoc,dp)
  dp.close()
  try:os.remove(lib)
  except:pass
 if int(utils.kodiver)<=16.7:
  dialog.ok(MainTitle+" : Update [COLOR green][B]finished[/B][/COLOR]",'[COLOR orange][B]!!!  HINT  !!![/B][/COLOR]','[B]Reboot[/B] Kodi to complete...','[B]Herstart[/B] Kodi ter afronding')
  Common.forceRefresh(melding=False)
 elif int(utils.kodiver)>16.7:
  utils.enableAddons(melding=False)
  time.sleep(0.5)
  choice=xbmcgui.Dialog().yesno(MainTitle+"[COLOR green][B] - success[/B][/COLOR]",' ','[B]IF[/B] add-ons do NOT work, you need to [B]reboot 1st[/B].','(een REBOOT van uw systeem is VEELAL wenselijk)',yeslabel='[COLOR lime]Reboot[/COLOR]',nolabel='[COLOR red]Continue[/COLOR]')
  if choice==1:
   time.sleep(1)
   Common.killKodi()
  elif choice==0:
   if int(utils.kodiver)>16.7:
    utils.enableAddons(melding=False)
    time.sleep(0.5)
    dialog.ok(MainTitle+" : [COLOR red]add-ons[/COLOR] [COLOR green][B]enabled[/B][/COLOR]",'[COLOR orange][B]!!!  TIP  !!![/B][/COLOR]','[B]Reboot[/B] Kodi to complete...','[B]Herstart[/B] Kodi ter afronding')
    xbmc.executebuiltin('ReloadSkin()')
 xbmc.executebuiltin("Container.Refresh")
 xbmc.sleep(5000)
def unlocker():
 dialog.ok(MainTitle+" - unlocker",' ','unlock advancedsettings for this build','[COLOR dimgray](+reset \'advancedsettings.xml\' -use at your own risk)[/COLOR]')
 addonmappie=xbmc.translatePath(os.path.join('special://home/userdata/'))
 advancedunlock=base64.b64decode('YWR2YW5jZWRzZXR0aW5ncy54bWw=')
 removed=True
 try:
  os.unlink(addonmappie+advancedunlock)
 except:
  removed=False
 if removed:
  dialog.ok(MainTitle+" - [B]UNLOCKED[/B]",'[COLOR green][B]!!!  FINISHED  !!![/B][/COLOR]','[B]Herstart[/B] Kodi ter afronding \'unlocker\' (force close)','[B]Reboot[/B] Kodi to complete \'unlocker\' (force close)')
  os._exit(1)
 else:
  dialog.ok(MainTitle+" - [B]OOOOOOPS[/B]",'[COLOR red][B]!!!  Failed  !!![/B][/COLOR]','[B]Nope![/B] helaas geen succes (niks te \'unlocken\')','[B]Nope![/B] close but no cigar  (nothing to \'unlock\')')
def XvbmcOc():
 myplatform=platform()
 Common.log("Platform: "+str(myplatform))
 if not myplatform=='linux':
  dialog.ok(MainTitle+" [B]-[/B] [COLOR lime]RPi[/COLOR] [B]-[/B] OverClock!",subtitleNope,nonlinux,nonelecNL)
  Common.log("none Linux OS ie. Open-/LibreELEC")
 else:
  Common.log("linux os")
  overclck.ocMenu()
def XvbmcDev():
 myplatform=platform()
 Common.log("Platform: "+str(myplatform))
 if not myplatform=='linux':
  dialog.ok(MainTitle+" [B]-[/B] [COLOR lime]RPi[/COLOR] [B]-[/B] #dev#",subtitleNope,nonlinux,nonelecNL)
  Common.log("none Linux OS ie. Open-/LibreELEC")
 else:
  Common.log("linux os")
  rpidevc.devMenu()
def disabled():
 Common.okDialog('[COLOR red][B]Sorry, disabled! [/B](for now)[/COLOR]','','[COLOR lime]goto [COLOR dodgerblue]http://bit.ly/XvBMC-NL[/COLOR], [COLOR dodgerblue]http://bit.ly/XvBMC-Pi[/COLOR] or [COLOR dodgerblue]https://bit.ly/XvBMC-Android[/COLOR] for more information...[/COLOR]')
def rejuvXvbmc():
 yes_pressed=Common.message_yes_no("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Reset![/B][/COLOR]",'Wilt u uw XvBMC \'build\' volledig opschonen (wipe) en Kodi Krypton [B]leeg[/B] her-configureren?','[COLOR dimgray]Please confirm that you wish you wipe clean your current configuration and reconfigure Kodi.[/COLOR]')
 if yes_pressed:
  addonPath=xbmcaddon.Addon(id=AddonID).getAddonInfo('path');addonPath=xbmc.translatePath(addonPath);
  xbmcPath=os.path.join(addonPath,"..","..");xbmcPath=os.path.abspath(xbmcPath);Common.log("rejuvXvbmc.main_XvBMC: xbmcPath="+xbmcPath);
  dir_exclude=('addons','Database','packages','userdata')
  sub_dir_exclude=('metadata.album.universal','metadata.artists.universal','metadata.common.imdb.com','metadata.common.musicbrainz.org','metadata.common.theaudiodb.com','metadata.common.themoviedb.org','metadata.themoviedb.org','metadata.tvdb.com','plugin.program.super.favourites','plugin.program.xvbmcinstaller.nl','repository.xvbmc','resource.language.nl_nl','script.xvbmc.updatertools','service.xbmc.versioncheck','skin.aeon.nox.spin','skin.eminence.2','skin.aczg','script.grab.fanart','service.library.data.provider','resource.images.recordlabels.white','resource.images.studios.coloured','resource.images.studios.white','xbmc.gui','script.skinshortcuts','script.module.simplejson','script.module.unidecode')
  file_exclude=('Addons26.db','Addons27.db','guisettings.xml','kodi.log','Textures13.db')
  keep_xvbmc=Common.message_yes_no("[COLOR white][B]"+AddonTitle+"[/B][/COLOR]",'Wilt u het XvBMC-NL basis \'framework\' handhaven na reset? Verwijderd alles behalve XvBMC (aanbeveling).','[COLOR dimgray](do you wish to keep XvBMC\'s default framework?)[/COLOR]')
  if keep_xvbmc:
   dir_exclude=dir_exclude+('addon_data','keymaps','media',)
   sub_dir_exclude=sub_dir_exclude+('inputstream.rtmp','keymaps','media','service.subtitles.addic7ed','service.subtitles.opensubtitles_by_opensubtitles','service.subtitles.opensubtitlesBeta','service.subtitles.podnapisi','service.subtitles.subscene',)
   file_exclude=file_exclude+('advancedsettings.xml','favourites.xml','profiles.xml','RssFeeds.xml','sources.xml','versiebld.txt','versiesp.txt','wizbld.txt','wizsp.txt',)
  else:
   dir_exclude=dir_exclude+('addon_data',)
   sub_dir_exclude=sub_dir_exclude+('inputstream.rtmp',)
   file_exclude=file_exclude+('advancedsettings.xml','RssFeeds.xml',)
   Superfavo=xbmc.translatePath(os.path.join(USERADDONDATA,'plugin.program.super.favourites','Super Favourites'))
   SkinShrtct=xbmc.translatePath(os.path.join(USERDATA,'addon_data','script.skinshortcuts'))
   try:
    shutil.rmtree(Superfavo)
   except Exception as e:Common.log("rejuvXvbmc.keep_xvbmc: XvBMC-vOoDoO @ "+str(e))
   try:
    shutil.rmtree(SkinShrtct)
   except Exception as e:Common.log("rejuvXvbmc.keep_xvbmc: XvBMC-vOoDoO @ "+str(e))
  dp.create("[COLOR white]"+AddonTitle+"[/COLOR] [COLOR red][B]- Reset![/B][/COLOR]",'Snelle XvBMC Krypton reset, even geduld...','','[COLOR dimgray](Quick XvBMC Krypton reset, please wait...)[/COLOR]')
  try:
   for root,dirs,files in os.walk(xbmcPath,topdown=True):
    dirs[:]=[dir for dir in dirs if dir not in sub_dir_exclude]
    files[:]=[file for file in files if file not in file_exclude]
    for file_name in files:
     try:
      dp.update(11,'','***Cleaning files...')
      os.remove(os.path.join(root,file_name))
     except Exception as e:Common.log("rejuvXvbmc.file_name: User files partially removed - "+str(e))
    for folder in dirs:
     if folder not in dir_exclude:
      try:
       dp.update(33,'','***Cleaning folders...')
       shutil.rmtree(os.path.join(root,folder))
      except Exception as e:Common.log("rejuvXvbmc.folder: User folders partially removed - "+str(e))
   dp.update(66,'','***Crap Cleaning...')
   Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS()
  except Exception as e:
   Common.log("rejuvXvbmc: User stuff partially removed - "+str(e))
   Common.message("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Error![/B][/COLOR]",'...DAT ging niet helemaal goed, controleer uw log...','[COLOR dimgray](XvBMC user files partially removed, please check log)[/COLOR]')
   sys.exit()
  dp.update(99,'','***Cleaning Crap...')
  Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();dp.close()
  dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR lime][B]- Reboot![/B][/COLOR]",'Kodi zal nu afsluiten','','[COLOR dimgray](shutdown Kodi now)[/COLOR]')
  os._exit(1)
 else:dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Cancelled![/B][/COLOR]",'Er is geen schone installatie gedaan...','','[COLOR dimgray](interrupted by user)[/COLOR]')
def WipeXBMC():
 if skin!="skin.estuary":
  dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Wipe![/B][/COLOR]",'selecteer eerst de standaard (Estuary) skin alvorens een volledige [B]\'wipe\'[/B] van uw Kodi uit te voeren.','','[COLOR dimgray](before Kodi wipe, select Estuary skin first)[/COLOR]')
  xbmc.executebuiltin("ActivateWindow(InterfaceSettings)")
  return
 else:
  choice=xbmcgui.Dialog().yesno("[COLOR lime][B]BELANGRIJK / IMPORTANT / HINT[/B][/COLOR]",'[B]let op: [/B]dit zal alles verwijderen van uw huidige Kodi installatie, weet u zeker dat u wilt doorgaan[B]?[/B]','','[COLOR dimgray](this will remove your current Kodi build, continue?)[/COLOR]',yeslabel='[COLOR lime][B]JA/YES[/B][/COLOR]',nolabel='[COLOR red]nee/nope[/COLOR]')
  if choice==1:
   dp.create("[COLOR white]"+AddonTitle+"[/COLOR] [COLOR red][B]- Wipe![/B][/COLOR]",'verwijder alles, even geduld...','','[COLOR dimgray](remove everything, please wait...)[/COLOR]')
   try:
    for root,dirs,files in os.walk(HOME,topdown=True):
     dirs[:]=[d for d in dirs if d not in EXCLUDES]
     for name in files:
      try:dp.update(11,'','***Cleaning files...');os.remove(os.path.join(root,name));os.rmdir(os.path.join(root,name))
      except:pass
     for name in dirs:
      try:dp.update(33,'','***Cleaning folders...');os.rmdir(os.path.join(root,name));os.rmdir(root)
      except:pass
    dp.update(66,'','***Crap Cleaning...')
    Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS()
   except:pass
   dp.update(99,'','***Cleaning Crap...')
   Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();dp.close()
   dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR lime][B]- Voltooid![/B][/COLOR]",'Kodi zal nu afsluiten...','','[COLOR dimgray](shutdown Kodi now)[/COLOR]')
   os._exit(1)
  elif choice==0:
   dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Cancelled![/B][/COLOR]",'Er is geen Kodi Krypton \'wipe\' uitgevoerd...','','[COLOR dimgray](interrupted by user)[/COLOR]')
def FRESHSTART(params):
 if int(utils.kodiver)>16.7:
  dialog.ok("[COLOR lime]"+MainTitle+"[/COLOR] [COLOR red][B]- NOPE![/B][/COLOR]",'[COLOR orange][B]NOTE:[/B][/COLOR]','[COLOR white]alleen voor oudere Kodi\'s dan Krypton (>17.0)[/COLOR]','[COLOR dimgray](for use with older Kodi\'s only (>17.0)[/COLOR]')
 else:
  Common.log("freshstart.main_XvBMC: "+repr(params));yes_pressed=Common.message_yes_no("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Remove[/B][/COLOR]",'Kodi terugzetten naar de standaard fabrieksinstellingen?','[COLOR dimgray](reset Kodi to factory defaults)[/COLOR]')
  if yes_pressed:
   addonPath=xbmcaddon.Addon(id=AddonID).getAddonInfo('path');addonPath=xbmc.translatePath(addonPath);
   xbmcPath=os.path.join(addonPath,"..","..");xbmcPath=os.path.abspath(xbmcPath);Common.log("freshstart.main_XvBMC: xbmcPath="+xbmcPath);failed=False
   dp.create("[COLOR white]"+AddonTitle+"[/COLOR] [COLOR red][B]- FreshStart![/B][/COLOR]",'terug naar fabrieksinstellingen, even geduld...','','[COLOR dimgray](factory reset Kodi, please wait...)[/COLOR]')
   try:
    for root,dirs,files in os.walk(xbmcPath,topdown=True):
     dirs[:]=[d for d in dirs if d not in EXCLUDES]
     dp.update(33,'','***Cleaning files+folders...')
     for name in files:
      try:os.remove(os.path.join(root,name))
      except:
       if name not in["Addons1.db","MyMusic7","MyVideos37.db","Textures1.db","xbmc.log"]:failed=True
       Common.log("XvBMC-Error removing file: "+root+" "+name)
     for name in dirs:
      try:os.rmdir(os.path.join(root,name))
      except:
       if name not in["Database","userdata"]:failed=True
       Common.log("XvBMC-Error removing folder: "+root+" "+name)
    dp.update(66,'','***Crap Cleaning...')
    Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS()
    if not failed:Common.log("freshstart.main_XvBMC: All user files removed, you now have a CLEAN install");Common.message("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR lime][B]- Voltooid![/B][/COLOR]",'\'FreshStart\' is klaar, verse Kodi beschikbaar na herstart...','[COLOR dimgray](\'FreshStart\' finished, fresh Kodi available after reboot)[/COLOR]')
    else:Common.log("freshstart.main_XvBMC: User files partially removed");Common.message("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR lime][B]- Voltooid![/B][/COLOR]",'\'FreshStart\' is klaar, verse Kodi beschikbaar na herstart...','[COLOR dimgray](\'FreshStart\' finished, fresh Kodi available after reboot)[/COLOR]')
   except:Common.message("[COLOR red][B]"+AddonTitle+"[/B][/COLOR]",'Problem found','Your settings have [B]not[/B] been changed');import traceback;Common.log(traceback.format_exc());Common.log("freshstart.main_XvBMC: NOTHING removed");sys.exit()
   dp.update(99,'','***Cleaning Crap...')
   Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();Common.REMOVE_EMPTY_FOLDERS();dp.close()
   dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR lime][B]- Reboot![/B][/COLOR]",'Kodi zal nu afsluiten','','[COLOR dimgray](shutdown Kodi now)[/COLOR]')
   os._exit(1)
  else:dialog.ok("[COLOR dodgerblue]"+AddonTitle+"[/COLOR] [COLOR red][B]- Cancelled![/B][/COLOR]",'Er is geen schone installatie gedaan...','','[COLOR dimgray](interrupted by user)[/COLOR]')
def addItem(name,url,mode,iconimage):
 u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
 ok=True
 liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
 liz.setInfo(type="Video",infoLabels={"Title":name})
 liz.setArt({'fanart':FANART})
 ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
 return ok
def get_params():
 param=[]
 paramstring=sys.argv[2]
 if len(paramstring)>=2:
  params=sys.argv[2]
  cleanedparams=params.replace('?','')
  if(params[len(params)-1]=='/'):
   params=params[0:len(params)-2]
  pairsofparams=cleanedparams.split('&')
  param={}
  for i in range(len(pairsofparams)):
   splitparams={}
   splitparams=pairsofparams[i].split('=')
   if(len(splitparams))==2:
    param[splitparams[0]]=splitparams[1]
 return param
def addDir(name,url,mode,iconimage,fanart,description):
 u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
 ok=True
 liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
 liz.setInfo(type="Video",infoLabels={"Title":name,"Plot":description})
 liz.setProperty("Fanart_Image",fanart)
 if mode==1:
  ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
 elif mode==2:
  ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
 elif mode==100:
  ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
 else:
  ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
 return ok
params=get_params()
url=None
name=None
mode=None
iconimage=None
fanart=None
description=None
try:
 url=urllib.unquote_plus(params["url"])
except:
 pass
try:
 name=urllib.unquote_plus(params["name"])
except:
 pass
try:
 iconimage=urllib.unquote_plus(params["iconimage"])
except:
 pass
try:
 mode=int(params["mode"])
except:
 pass
try:
 fanart=urllib.unquote_plus(params["fanart"])
except:
 pass
try:
 description=urllib.unquote_plus(params["description"])
except:
 pass
Common.log("EPiC "+str(AddonTitle))
if mode==None or url==None or len(url)<1:
 mainMenu()
elif mode==1:
 wizard(name,url)
elif mode==10:
 XvBMCtools1()
elif mode==20:
 XvBMCmaint()
elif mode==30:
 XvBMCrpi()
elif mode==2:
 Common.AboutXvBMC()
elif mode==3:
 Common.closeandexit()
elif mode==4:
 Common.okDialog(subtitleNope,'sorry, nothing todo...','with kind regards, team [COLOR green]XvBMC Nederland[/COLOR]')
elif mode==11:
 nursemaid.Fix_Special(url)
elif mode==12:
 nursemaid.AddonsEnable()
elif mode==13:
 addon_able.setall_enable()
elif mode==14:
 nursemaid.EnableRTMP()
elif mode==15:
 Common.killKodi()
elif mode==16:
 Common.KODIVERSION(url)
elif mode==17:
 nursemaid.xvbmcLog()
elif mode==8:
 resolveUrl_settings()
elif mode==18:
 Urlresolver_settings()
elif mode==19:
 unlocker()
elif mode==22:
 nursemaid.clearCache()
elif mode==23:
 nursemaid.deleteThumbnails()
elif mode==25:
 nursemaid.autocleanask()
elif mode==26:
 nursemaid.purgePackages()
elif mode==27:
 Common.forceRefresh(melding=True)
elif mode==28:
 nursemaid.AddonsDatabaseRemoval()
elif mode==29:
 utils.enableAddons(melding=True)
elif mode==31:
 nursemaid.PiCCleaner()
elif mode==32:
 XvbmcOc()
elif mode==33:
 XvbmcDev()
elif mode==40:
 XvBMCtools2()
elif mode==41:
 rejuvXvbmc()
elif mode==42:
 WipeXBMC()
elif mode==43:
 FRESHSTART(params)
elif mode==44:
 disabled()
elif mode==45:
 name='repository.xvbmc-4.2.0.zip'
 url=base64.b64decode(repos)
 storeLoc=xbmc.translatePath(os.path.join('special://home/addons','packages'))
 unzipLoc=os.path.join(HOME,'addons')
 customwizard(name,url,storeLoc,unzipLoc)
elif mode==46:
 url=base64.b64decode(base)+'triple-x/xXxvbmc.zip'
 wizard(name,url)
elif mode==69:
 xbmc.executebuiltin('ActivateWindow(10025,"plugin://plugin.program.super.favourites/?folder=xXx",return)')
elif mode==70:
 name='plugin.program.super.favourites-1.0.59.zip'
 url=base64.b64decode(base)+'plugin.program.super.favourites/'
 storeLoc=xbmc.translatePath(os.path.join('special://home/addons','packages'))
 unzipLoc=os.path.join(HOME,'addons')
 customwizard(name,url,storeLoc,unzipLoc)
elif mode==100:
 locatie=USERDATA
 name1='rpi-sp'
 name2='rpi-service'
 fileexchange(url,name2+'.txt',locatie)
 wizard(name,url+name1+'.zip')
"""
    IF you copy/paste XvBMC's -default.py- please keep the credits -2- XvBMC-NL, Thx.
"""
xbmcplugin.endOfDirectory(int(sys.argv[1]))