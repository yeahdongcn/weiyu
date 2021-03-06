#!/bin/bash

UTIL_DIR="$( cd "$( dirname ${BASH_SOURCE[0]} )" && pwd )"

cd "${UTIL_DIR}/.."

for subdir in examples luohua weiyu util; do
    [ -d "${subdir}" ] && find "${subdir}" -name '*.py' -type f | xargs pep8
done


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
