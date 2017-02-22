#!/bin/bash
tar cfvz "client_install-`date +%Y%m%d-%H%M%S`".tar.gz client_install pack_client_install.sh unpack_client_install
mv client_install-* ./backup/



