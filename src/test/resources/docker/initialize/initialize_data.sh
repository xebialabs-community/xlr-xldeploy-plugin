#!/bin/sh
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

####################### XLD server data


wget --http-user=admin --http-password=admin --auth-no-challenge \
     --header="Accept: application/json" \
     --header="Content-type: application/json" \
     --post-file=$SCRIPTPATH/data/server-configs.json \
    http://localhost:5516/repository/cis -O /dev/null


##### Insert template

wget --http-user=admin --http-password=admin --auth-no-challenge \
     --header="Accept: application/json" \
     --header="Content-type: application/json" \
     --post-file=$SCRIPTPATH/data/ispw-template.json \
    http://localhost:5516/api/v1/templates/import -O /dev/null
