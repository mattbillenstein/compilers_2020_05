#!/bin/bash

set -eo pipefail

./script_models.py 2> /dev/null
./func_models.py 2> /dev/null
./type_models.py 2> /dev/null

for f in tests/Script/*.wb; do
    echo
    echo '=========================='
    echo
    name=$(basename $f)
    echo "time SillyWabbit/wabbit.py $f 2> /dev/null > /tmp/$name-silly.out"
    time SillyWabbit/wabbit.py $f 2> /dev/null > /tmp/$name-silly.out
    echo
    echo "time python3 -m wabbit.interp $f 2> /dev/null > /tmp/$name-mattb.out"
    time python3 -m wabbit.interp $f 2> /dev/null > /tmp/$name-mattb.out
    echo
    echo "diff /tmp/$name-silly.out /tmp/$name-mattb.out"
    diff /tmp/$name-silly.out /tmp/$name-mattb.out
done

echo 'PASSED'
