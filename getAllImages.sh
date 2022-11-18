#!bin/bash

OIFS="$IFS"
IFS=$'\n' 

for topFolder in *; do
  cd $topFolder
  for id in *; do
    mv $id/image.webp ../../all_Images/${id}.webp
    echo "${id} moved"
  done
  cd ..
done


IFS="$OIFS"