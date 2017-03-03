#!/bin/sh
#echo "lightdm: start session-cleanup.sh"
# erst testen, ob "keinpasswort" aktiv ist
test "$USER" = "keinpasswort" || exit 0;


# cleanup-script soll nur weiterlaufen, wenn
# keinpasswort durch aufs geschützt wird.
#immutable=`mount -l -t aufs |grep 'none on /home/keinpasswort type aufs (rw,br:/home/.keinpasswort_rw:/home/keinpasswort)'`
immutable=`mount -l -t aufs |grep 'none on /home/keinpasswort type aufs'`
test -n "$immutable" || exit 0;

# Lösch-Funktion, welcher zusätzliche find-Argumente übergeben werden können
loeschen (){
  # Verwaltungs-Objekte von aufs
  no_aufs="! -name .wh..wh.aufs ! -name .wh..wh.orph ! -name .wh..wh.plnk"
  # Zusätzliches find-Argument speichern
  zusatz="$1"
  # Wird dieses Script als root ausgeführt, kann das folgende "rm -rf" sehr gefährlich werden --
  # insbesondere zu Testzwecken auf einem normalen Arbeitsrechner. Mit der folgenden Kombination
  # ist sichergestellt, dass wirklich nur der Inhalt von .keinpasswort_rw gelöscht wird.
  # !! nächster Absatz ist wichtig!
  # Es müssen erst alle Prozesse gestoppt werden (fuser -k), die auf /home/keinpasswort zugreifen, danach kann die Glasscheibe getrennt
  # werden und der Inhalt gelöscht werden. Mit 16.04 funktioniert der alte Mechnismus nicht mehr. Es kommt zur Löschung von
  # Konfigdateien (.config), die den Account keinpasswort zum nächsten Reboot unbrauchbar machen.
  # Wichtig: am Ende wieder die Glasscheibe einziehen, damit /home/keinpasswort geschützt bleibt.
  fuser -k -m /home/keinpasswort
  umount /home/keinpasswort
  cd /home/.keinpasswort_rw && find . -maxdepth 1 -mindepth 1 $no_aufs $zusatz -print0|xargs -0 rm -rf
  mount /home/keinpasswort

  # NetworkManager Connections schützen
  rm /etc/NetworkManager/system-connections/*
  cp /etc/NetworkManager/connections_backup/* /etc/NetworkManager/system-connections/
  nmcli connection reload
}

# Inhalt von .keinpasswort_rw beim Login löschen. Das .pulse-Verzeichnis muss stehen
# bleiben, da es sonst bei direkter Neuanmeldung zu Sound-Problemen kommen kann.
loeschen "! -name .pulse"

exit 0

