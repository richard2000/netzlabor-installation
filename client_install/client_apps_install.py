#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 19:34:29 2016

@author: Richard Wegers
"""
import os
import getpass
import apt
import json
import glob
#from subprocess import call


DEBUG = 0 # Default 0; 1 schaltet Debug-Ausgaben an.

getinput=0
user= getpass.getuser()
print(user)
raumserver = '192.168.21.91'
cache = apt.Cache()

# WICHTIGE VARIABELN
# PROGRAMME
# standard_apps: Standard-Pakete, die zum Betriebssystem gehören
# network_apps: Labor spezifische Pakete, die primär für den Netzwerkunterricht eingesetzt werden
# remove_apps: Pakete, die deinstalliert werden sollen. z.B. Spiele

# Text-Dateien
# config_files: reine Konfigurationsdateien, die nicht ausführbar gemacht werden (chmod 644)
# script_files: Scripte, die zusätzlich noch ausführbar gemacht werden müssen (chmod 700)

install_paket_liste = "install_paket_liste.json"

# reine Config-Files, die nicht ausführbar gemacht werden müssen.
config_files = (
    "/etc/default/sipwitch",
    "/etc/default/grub",
    "/etc/hosts",
    "/etc/hostname",
    "/etc/init.d/rc.local",
    "/etc/lightdm/lightdm.conf",
    "/etc/lightdm/lightdm-gtk-greeter.conf",
    "/etc/ssh/sshd_config",
    
    "/etc/xdg/autostart/conky.desktop",    
    "/etc/xdg/user-dirs.defaults",
    "/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml",
    "/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml",
#    "/etc/xdg/xdg-xubuntu/lightdm/lightdm-gtk-greeter.conf", # s. /etc/skel
#    "/etc/xdg/xdg-xubuntu/lightdm/lightdm-gtk-greeter.conf, # s. /etc/skel
#    "/etc/xdg/xdg-xubuntu/Terminal/terminalrc", # s. /etc/skel

    "/etc/modules",
    "/etc/quagga/daemons",
    "/etc/quagga/debian.conf",
    "/etc/quagga/ospfd.conf",
    "/etc/quagga/ripd.conf",
    "/etc/quagga/zebra.conf",   
    "/etc/sysctl.d/60-hardlink-restrictions-disabled.conf",
    "/usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy"
    
)

# Scripte, die ausführbar gemacht werden müssen.
script_files = (
    "/etc/lightdm/session-cleanup.sh",
    "/etc/lightdm/session-setup.sh",
    "/usr/local/bin/delldapuser.pl",
    "/usr/local/bin/cleanup-keinpasswort.sh"
)

# Pakete, die für das System nachinstalliert werden müssen
#    "adobe-flash-properties-gtk",
#    "adobe-flashplugin",
#    "sipwitch-plugin-forward", # SIP-Proxy; muss vorher installiert werden, damit config-Dateien überschrieben werden können.


ppa_sources = (
    "/etc/apt/source.list.d/ravefinity-project-ubuntu-ppa-xenial.list",
    "libreoffice-ubuntu-libreoffice-5-1-xenial.list"
)

local_users = (
    "keinpasswort",
    "lehrer"
)

#''''''''''''''
# Hilfsroutinen
#''''''''''''''
def debug_print(str):
    if DEBUG == 1:
        print ("DEBUG: "+str)

def getinput():
    yes = set(['ja','j', 'J'])
    no = set(['nein','n', '']) # default nein

    choice = input().lower()
    if choice in yes:
       return True
    elif choice in no:
       return False
    else:
       print("Bitte 'ja' oder 'nein' eingeben")
       
# Appliste aus json-Konfigurationsfile holen und Inhalt als app_list zurückliefern  
def get_app_list(file):
    debug_print("get_task: "+ file)
    f=open(file)
    data = json.load(f)
    debug_print (data)
    app_list = data['standard_apps']
    return app_list

# Zeigt zur Kontrolle die Liste von Apps an inkl. der Kommentare
def print_apps_list (app_list):
    k=0
    print ("{0:<34}{1}".format('    Paket',       'Kommentar'))
    print ("{0:<34}{1}".format('    -----------', '-----------'))
    for i in app_list :
        k+=1
        print ("{k:2}: {app:<30}{comment}".format(k=k, app=i, comment=app_list[i]))      
  
# Installation mehrerer Pakete
def install_apps(apps):
    for app in apps:
        if os.system("dpkg -s {a} | grep -c -i \"ok installed\">/dev/null".format(a=app))!=0:
#            if os.system ("dpkg -l | grep -i "+i+">/dev/null")==0:
                print ("\tjetzt wird {a} INSTALLIERT!\n".format(a=app))
                print ("os.system (\"apt-get install {a} -y\") ".format(a=app))
                os.system ("apt-get install {a} -y".format(a=app))
                print ("######################-------------------------++++++++++++++++++++++++++-------------------------######################")
        else:
                print ("\t{a} ist bereits installiert.\n".format(a=app))

# Deinstallation mehrerer Pakete
def deinstall_apps(apps):
    for app in apps:
        if cache[app].is_installed:
            print ("Paket: {a} ist installiert und wird jetz DEinstalliert.".format(a=app))
            os.system ("apt-get remove {a} -y".format(a=app))
        else:
            print ("\t{a} ist NICHT installiert.".format(a=app))


# Datei sichern und kopieren
# app: Dateipfad; mode: chmod Parameter z.B 644 (read all) oder 700 (exe)
def backup_move (app, mode):
    if not os.path.isfile( "{a}.org".format(a=app)):
    #if not os.path.isfile( app+".org" ):
        if os.path.isfile(app):
            print ("\n\tOriginale "+app+"-Datei sichern!\n")
            os.system ("mv {a} {a}.org".format(a=app))
            #os.system ("mv "+app+" "+app+".org")
        print ("\tNeue "+app+"-Datei kopieren!\n")
        os.system ("cp .{a} {a}".format(a=app))
        #os.system ("cp ."+app+" "+app)
        os.system ("chmod {m} {a}".format(m=mode,a=app))
        #os.system ("chmod 644 "+i)
    else:
        print ("\n\t{a}-Datei wurden bereits angelegt.\n".format(a=app))

# Hilfsfunktion, um Sicherungskopien zu erstellen
# Datei sichern und kopieren
def backup (app):
    print ("\n\tOriginale {a}-Datei sichern!\n".format(a=app))
    os.system ("cp {a} {a}-`date +%Y%m%d-%H%M%S`-`stat -c '%G-%U-%a' {a}`".format(a=app))
    #os.system ("cp "+app+" "+app+"-`date +%Y%m%d-%H%M%S`-`stat -c '%G-%U-%a' "+app+"`")


# Hilfsfunktion, um Texte an eine Datei anzuhängen
# file: Pfad der Datei
# in_string: Inhalt, der angehängt werden soll als Dictionary
def write2file(file, in_string, mode):
    mytxt=""
    with open(file, mode) as myfile:
        for i in in_string:
            mytxt=mytxt + str(i) +"\n"
        print(mytxt, file=myfile)

###################
# BEGINN 
###################
# Schritt 0: Abklären, ob root-Rechte existieren, wenn nicht passiert nichts
if not os.getuid() == 0:
    print ("\t## Fehler: root ist nicht aktiv. \n")
    print ("\tDie folgenden Befehle müssen können nur ausgeführt werden,\n\twenn root aktiv ist.\n")
    print ("\tBitte mit \"sudo su\" zu root wechseln.\n\n")
    quit()
else:
    print ("\troot ist aktiv Pakete können installiert werden.\n")
        #("dpkg -s sudo | grep -i \"ok installed\">/dev/null")
    if os.system("dpkg -s sudo| grep -i \"ok installed\">/dev/null")==0:
        print ("\tDie folgenden drei Befehle müssen MANUELL ausgeführt werden.\n\n")
        print ("\t\texport SUDO_FORCE_REMOVE=yes\n")
        print ("\t\tapt-get install sudo-ldap\n")
        print ("\t\texport SUDO_FORCE_REMOVE=no\n\n")

#################################################
# Schritt 1: Erstmal alle Pakete installieren, die für den LDAP-Client gebraucht werden
print ("\n\n\tGrundinstallation: Es werden die nötigen Pakete installiert, sowie überflüssige Pakete deinstalliert.\n")
print ("\nDie folgenden Grundpakete werden als nächstes installiert:")
standard_apps= get_app_list (install_paket_liste, 'standard_apps')
print_apps_list(standard_apps)

print ("\n\n\tDie folgenden Grundpakete werden als nächstes DEINSTALLIERT:")
remove_apps= get_app_list (install_paket_liste, 'remove_apps')
print_apps_list(remove_apps)

print ("\n\n\tSollen die Grundpakete für Client de-/installiert werden? [j/n]: ")

if getinput():
    print ("\n UPDATE Sources\n")
    # sipwitch ppa integrieren
#    os.system ("add-apt-repository ppa:gnutelephony/ppa")
    # ambiance theme ppa integrieren
    if not os.path.isfile("/etc/apt/sources.list.d/ravefinity-project-ubuntu-ppa-xenial.list"):
        os.system ("add-apt-repository ppa:ravefinity-project/ppa")
    if not os.path.isfile("/etc/apt/source.list.d/libreoffice-ubuntu-libreoffice-5-1-xenial.list"):
        os.system ("add-apt-repository ppa:libreoffice/libreoffice-5-1")
        
    os.system ("apt-get update")
    print ("\n INSTALLATIONEN\n")
    install_apps(standard_apps)
    print ("\n DEINSTALLATIONEN\n")
    deinstall_apps(remove_apps)
    print ("\n Upgrade alles auf den neuesten Stand bringen")
    os.system ("apt-get -y upgrade")
    print ("\n\t AUFRÄUMEN")
    os.system ("apt-get autoremove")
else:
    print ("\tEs werden keine Standard-Pakete installiert.\n")


print ("\tEs wurden alle notwendigen Pakete installiert.\n")

# Optionale Pakete nachinstallieren erst, wenn lokale User eingerichtet wurden, da User Rechte bekommen müssen
print ("\nDie folgend optionalen Pakete werden als nächstes installiert:")
network_apps= get_app_list (install_paket_liste, 'network_apps')
print_apps_list(network_apps)

print ("\n\n\tNetzwerklabor-Pakete (Tools) für die Clients installieren? [j/n]: ")
if getinput():
    install_apps(network_apps)
    os.system ("dpkg-reconfigure wireshark-common")
    for user in local_users:
        if os.system ("id {u} | grep -c wireshark>/dev/null".format(u=user))!=1:
            print ("\tUser: {u} noch nicht in der Gruppe \"wireshark\". User wird hinzugefügt.\n".format(u=user))
            os.system ("usermod -a -G wireshark {u}".format(u=user))
        else:
            print ("\tUser: {u} ist bereits in der Gruppe \"wireshark\". Nichts passiert.\n".format(u=user))
        if os.system ("id {u} | grep -i vboxusers>/dev/null".format(u=user))!=1:
            print ("\tUser: {u} noch nicht in der Gruppe \"vbosusers\". User wird hinzugefügt.\n".format(u=user))
            os.system ("usermod -a -G vboxusers {u}".format(u=user))
        else:
            print ("\tUser: {u} ist bereits in der Gruppe \"vboxusers\". Nichts passiert.\n".format(u=user))
else:
    print ("\tEs werden keine optionalen Pakete installiert.\n")

# Alle Schnittstellen inkl. MACs ausgeben    
for fn in glob.glob('/sys/class/net/*/address'):
    iftype= fn.split('/')[4]
    macaddr = open(fn).readline()
    print ("Bezeichner: {type:6} MAC: {mac:13}".format(type=iftype, mac=macaddr))

print ("Installationsdurchlauf abgeschlossen. Beliebige Taste drücken zum Beenden.")
if getinput():
    print ("")


