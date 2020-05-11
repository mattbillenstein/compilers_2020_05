#!/bin/bash

set -eo pipefail

echo "./script_models.py 2> /dev/null"
./script_models.py 2> /dev/null
echo "./func_models.py 2> /dev/null"
./func_models.py 2> /dev/null
echo "./type_models.py 2> /dev/null"
./type_models.py 2> /dev/null

function test_file() {
    f=$1
    name=$(basename $f)
    echo
    echo '=========================='
    echo
    # just make sure we can parse and generate source
    echo "python3 -m wabbit.source $f > /dev/null"
    python3 -m wabbit.source $f > /dev/null
    echo "time SillyWabbit/wabbit.py $f 2> /dev/null > /tmp/$name-silly.out"
    time SillyWabbit/wabbit.py $f 2> /dev/null > /tmp/$name-silly.out
    echo
    echo "time python3 -m wabbit.interp $f 2> /dev/null > /tmp/$name-mattb.out"
    time python3 -m wabbit.interp $f 2> /dev/null > /tmp/$name-mattb.out

    echo
    echo "python3 -m wabbit.c < $f 2> /dev/null > /tmp/$name-mattb.c"
    python3 -m wabbit.c < $f 2> /dev/null > /tmp/$name-mattb.c
    echo "clang /tmp/$name-mattb.c -o /tmp/$name-mattb.c.exe"
    clang /tmp/$name-mattb.c -o /tmp/$name-mattb.c.exe
    echo "/tmp/$name-mattb.c.exe > /tmp/$name-mattb.c.out"
    /tmp/$name-mattb.c.exe > /tmp/$name-mattb.c.out

    echo
    echo "diff /tmp/$name-silly.out /tmp/$name-mattb.out"
    diff /tmp/$name-silly.out /tmp/$name-mattb.out
}

# everything except enums...  mandel last...
for f in $(ls tests/Script/*.wb tests/Func/*.wb | grep -v mandel) $(grep -L '::' tests/Type/*.wb); do
    test_file $f
done

test_file tests/Script/mandel_loop.wb
test_file tests/Func/mandel.wb

echo 'PASSED'
