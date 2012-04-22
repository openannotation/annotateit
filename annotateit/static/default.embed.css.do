redo-ifchange "${2}.less"
lessc "${2}.less" "${3}"
gsed -r -i'' -e 's/;/ !important;/' -e 's/(@[^!]+)!important;/\1;/' "${3}"