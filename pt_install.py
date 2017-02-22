#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:58:36 2017

@author: Richard Wegers
"""

import os

pt_file="/usr/share/applications/packettracer.desktop"
packettracer_desktop=[
    "[Desktop Entry]",
    " Name= Packettracer",
    " Comment=Networking",
    " GenericName=Cisco Packettracer",
    " Exec=/opt/packettracer/packettracer",
    " Icon=/usr/share/icons/packettracer.jpeg",
    " StartupNotify=true",
    " Terminal=false",
    " Type=Application"
]

profile="/etc/profile"
profile_text=[
    "PT6HOME=/opt/pt",
    "export PT6HOME"
]

tmp_path="/tmp"
pt_path="/PacketTracer611Student"
deb_path="/var/cache/apt/archives"

def write2file(file, in_string, mode):
    mytxt=""
    with open(file, mode) as myfile:
        for i in in_string:
            mytxt=mytxt + str(i) +"\n"
        print(mytxt, file=myfile)


if not os.getuid() == 0:
    print ("\t## Fehler: root ist nicht aktiv. \n")
    print ("\tDie folgenden Befehle müssen können nur ausgeführt werden,\n\twenn root aktiv ist.\n")
    print ("\tBitte mit \"sudo su\" zu root wechseln.\n\n")
    quit()
install_path=os.getcwd()
print("Start-Pfad: "+install_path)    
os.system("cp pt_pakete.tar.gz "+deb_path)
os.chdir(deb_path)
os.system("tar -zxvf pt_pakete.tar.gz")

os.system("sudo dpkg --add-architecture i386")
os.system("sudo apt-get update")
# nächste Zeile, um Fehler zu vermeiden
os.system("sudo dpkg --configure -a")
os.system("sudo apt-get install libc6:i386")
os.system("sudo apt-get install lib32z1 lib32ncurses5 lib32bz2-1.0")
os.system("sudo apt-get install libnss3-1d:i386 libqt4-qt3support:i386 libssl1.0.0:i386 libqtwebkit4:i386 libqt4-scripttools:i386")

print("Wechsele nach"+install_path)
os.chdir(install_path)
os.system("cp CiscoPacketTracer6.1.1forLinux.tar.gz "+tmp_path)
os.system("tar -zxvf CiscoPacketTracer6.1.1forLinux.tar.gz")

print ("Wechsle in Installationpfad")
os.chdir(tmp_path+pt_path)
print (os.getcwd())
os.system("sudo cp /etc/profile /etc/profile_backup_PT")
os.system("sudo ./install")
os.system("sudo cp /etc/profile_backup_PT /etc/profile")
write2file(profile, profile_text, "a")
write2file(pt_file, packettracer_desktop, "w")



