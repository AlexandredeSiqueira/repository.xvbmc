#!/usr/bin/python
#-*- coding: utf-8 -*-
import os,xbmc,xbmcaddon,xbmcgui,xbmcplugin
import utils
AddonID='script.xvbmc.updatertools'
ADDON=xbmcaddon.Addon(id=AddonID)
dialog=xbmcgui.Dialog()
MainTitle="[COLOR lime][B]XvBMC[/B] Update[/COLOR]"
Subtitle='[COLOR white]There is a new [B]XvBMC[/B] update[/COLOR]'
Updatevraag='[COLOR white]Do you whish to update XvBMC [COLOR orange][B]now[/B][/COLOR], or later[B]?[/B][/COLOR]'
NU="[COLOR lime]NOW[/COLOR]"
misschien="[COLOR red]Later [B] :'([/B][/COLOR]"
xbmc.sleep(5000)
updateCheck,versie=utils.checkUpdate()
if updateCheck=='EminenceUpdate':
 yes_pressed=dialog.yesno(MainTitle,Subtitle+'[COLOR white] for your [B]Eminence[/B][/COLOR]',Updatevraag,'',yeslabel=NU,nolabel=misschien)
 if yes_pressed:
  xbmc.executebuiltin('ActivateWindow(10001,plugin://script.xvbmc.updatertools/,return)')
 else:
  dialog.ok(MainTitle,'[COLOR white]You can update [B]XvBMC[/B] the next time you reboot...[/COLOR]','','')
elif updateCheck=='NoxSpinUpdate':
 yes_pressed=dialog.yesno(MainTitle,Subtitle+'[COLOR white] for your [B]NoxSpin[/B][/COLOR]',Updatevraag,'',yeslabel=NU,nolabel=misschien)
 if yes_pressed:
  xbmc.executebuiltin('ActivateWindow(10001,plugin://script.xvbmc.updatertools/,return)')
 else:
  dialog.ok(MainTitle,'[COLOR white]You can update [B]XvBMC[/B] the next time you reboot...[/COLOR]','','')
elif updateCheck=='PortableUpdate':
 yes_pressed=dialog.yesno(MainTitle,Subtitle+'[COLOR white] for your [B]Portable[/B][/COLOR]',Updatevraag,'',yeslabel=NU,nolabel=misschien)
 if yes_pressed:
  xbmc.executebuiltin('ActivateWindow(10001,plugin://script.xvbmc.updatertools/,return)')
 else:
  dialog.ok(MainTitle,'[COLOR white]You can update [B]XvBMC[/B] the next time you reboot...[/COLOR]','','')
elif updateCheck=='RPiUpdate':
 yes_pressed=dialog.yesno(MainTitle,Subtitle+'[COLOR white] for your [B]RPi[/B][/COLOR]',Updatevraag,'',yeslabel=NU,nolabel=misschien)
 if yes_pressed:
  xbmc.executebuiltin('ActivateWindow(10001,plugin://script.xvbmc.updatertools/,return)')
 else:
  dialog.ok(MainTitle,'[COLOR white]You can update [B]XvBMC[/B] the next time you reboot...[/COLOR]','','')
elif updateCheck=='ZeitgeistUpdate':
 yes_pressed=dialog.yesno(MainTitle,Subtitle+'[COLOR white] for your [B]Zeitgeist[/B][/COLOR]',Updatevraag,'',yeslabel=NU,nolabel=misschien)
 if yes_pressed:
  xbmc.executebuiltin('ActivateWindow(10001,plugin://script.xvbmc.updatertools/,return)')
 else:
  dialog.ok(MainTitle,'[COLOR white]You can update [B]XvBMC[/B] the next time you reboot...[/COLOR]','','')