#!/bin/bash

if [[ -e MadLoop5_resources.tar && ! -e MadLoop5_resources ]]; then
tar -xf MadLoop5_resources.tar
fi
k=run1_app.log
script=refine_splitted.sh
# Argument
# 1st argument the Directory name
grid_directory=$1;
# 2st argument Directory where to find the grid input
base_directory=$2; 
# 3st argument the offset
offset=$3;


# prepare the directory where to run
if [[ ! -e $grid_directory ]]; then
    # Do not exists     
    mkdir $grid_directory;
else
   rm -rf $grid_directory/$k;
   rm -rf $grid_directory/input_app.txt;
   rm -rf $grid_directory/ftn25;
   rm -rf $grid_directory/ftn26;
fi
# handle input file
if [[ -e $base_directory ]]; then
    cp $base_directory/ftn26 $grid_directory/ftn25;
    cp $base_directory/input_app.txt $grid_directory/input_app.txt;
elif [[ -e ./ftn26 ]]; then
    cp ./ftn26 $grid_directory/ftn25;
    cp ./input_app.txt $grid_directory/input_app.txt;
else
    exit 1;
fi

# Move to the running directory
cd $grid_directory;

# Put the correct offset
rm -f moffset.dat >& /dev/null;
echo   $offset > moffset.dat;

# run the executable. The loop is design to avoid
# filesystem problem (executable not found)
for((try=1;try<=16;try+=1)); 
do
    ../madevent >> $k <input_app.txt;
    if [ -s $k ]
    then
        break
    else
        echo $try > fail.log 
    fi
done
echo "" >> $k; echo "ls status:" >> $k; ls >> $k
cd ../

