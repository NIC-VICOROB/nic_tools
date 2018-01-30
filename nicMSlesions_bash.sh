#!/bin/bash

# --------------------------------------------------
# nicMSlesions
#
# Sergi Valverde 2018
# https://github.com/sergivalverde/nicMSlesions
#
# --------------------------------------------------

# script variables
RUNMACHINE='true'
DOCKERMACHINE='docker'
UPDATEDOCKER='false'
if [ $# == 0 ];DATE=`date '+%Y-%m-%d-%H:%M'`
echo $DATE
# helper function to show the menu help
display_help() {
    echo " "
    echo "nicMSLesions"
    echo "-g | --gpu                  --> Use GPU instead of CPU (requires nvidia-docker)"
    echo "-u | --update               --> update software to the latest version"
    echo "-h | --help                 --> shows this message"
    echo " "
}


# the data folder in the host machine has to be mapped into the docker machine before
# running the script using -d /path/to/data. Other options are:
# -g use GPU
# -u update the docker image before running it
# -h show the help menu

while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -d|--data)
            DATAPATH="$2"
            RUNMACHINE='true'
            shift
            shift
            ;;
        -g|--gpu)
            DOCKERMACHINE="nvidia-docker"
            shift
            ;;
        -u|--update)
            UPDATEDOCKER="true"
            shift
            ;;
        -h|--help)
            display_help
            shift
            exit
            ;;
        --default)
            echo "Incorrect option/s..."
            display_help
            exit
    esac
done

# update Docker image if the update option is selected
if [ $UPDATEDOCKER == 'true' ];
then
    echo "updating the Docker image"
    docker pull nicvicorob/mslesions:latest
fi

# run the docker image
if [ $RUNMACHINE == 'true' ];
then
    echo  "##################################################"
    echo  "# ------------                                   #"
    echo  "# nicMSlesions (docker edition)                  #"
    echo  "# ------------                                   #"
    echo  "# MS WM lesion segmentation                      #"
    echo  "#                                                #"
    echo  "# -------------------------------                #"
    echo  "# (c) Sergi Valverde 2018                        #"
    echo  "# Neuroimage Computing Group                     #"
    echo  "# -------------------------------                #"
    echo  "##################################################"
    echo " "
    eval $DOCKERMACHINE run -ti  \
         -v $PWD/config:/src/config:rw \
         -v $PWD/models:/src/nets:rw \
         -v /:/data:rw \
         nicvicorob/mslesions:latest python -u nic_train_network_batch.py --docker | \
         tee $PWD/logs/$DATE.txt
fi
