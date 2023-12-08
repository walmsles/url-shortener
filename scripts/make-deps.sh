#!/bin/bash

for folder in $(ls -d ${WORKDIR:-${PWD}}/services/* | grep -v __pycache__)
do
    if [[ -d ${folder} ]]; then
        group=$(basename ${folder})

        # check if service group exists
        poetry show --with=${group} --quiet
        group_exists=$?
        all_groups=""
        if [[ $group_exists -eq 0 ]]; then
            # export main dependencies AND specific group dependencies
            echo creating requirements in ${folder}
            all_groups="${all_groups} --with=${group}"
            poetry export --without-hashes --with=${group} --with main > ${folder}/requirements.txt
        else
            # export main only (to avoid poetry errors)
            echo creating requirements in ${folder}
            poetry export --without-hashes --with main > ${folder}/requirements.txt
        fi
    fi
done

# export
echo "poetry export --without-hashes --with dev $all_groups > ${WORKDIR:-${PWD}}/tests/requirements.txt"
poetry export --without-hashes --with dev $all_groups > ${WORKDIR:-${PWD}}/tests/requirements.txt
