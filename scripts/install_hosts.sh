#!/bin/bash
# This script will install the hosts file to /etc/hosts
CM_ENTRY="127.0.0.1 cm.local api.cm.local img.cm.local minio.cm.local mailhog.cm.local"

add_if_host_not_exists () {
    if grep -q "$CM_ENTRY" /etc/hosts; then
        echo "Hosts file already contains CM entry"
    else
        echo "Adding CM entry to hosts file"
        sudo -- sh -c -e "echo '$CM_ENTRY' >> /etc/hosts";
    fi
}

add_if_host_not_exists

echo "CM hosts file installed successfully! You can now access the application at https://cm.local"
