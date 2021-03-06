#!/bin/bash

# --------------------------------------------------
# nicMSlesions
#
# Sergi Valverde 2018
# https://github.com/sergivalverde/nicMSlesions
#
# --------------------------------------------------

# script variables
RUNMACHINE='false'
DOCKERMACHINE='docker run'
UPDATEDOCKER='false'
CURRENT_FOLDER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATE=`date '+%Y-%m-%d-%H:%M'`

# get the DOCKER_VERSION
source docker_version
echo "--------------------------------------------------"  | tee -a $CURRENT_FOLDER/logs/$DATE.txt
echo "VERSION: " $DOCKER_VERSION  | tee -a $CURRENT_FOLDER/logs/$DATE.txt
echo "DATE: " $DATE | tee -a $CURRENT_FOLDER/logs/$DATE.txt
echo "--------------------------------------------------"  | tee -a $CURRENT_FOLDER/logs/$DATE.txt


# helper function to show the menu help
display_help() {
    echo " "
    echo "nicMSLesions -d /path/to/data/ [options]"
    echo "-d | --data  /path/to/data  --> path to input data (mandatory)"
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

if [ $# == 0 ];
then
    display_help
fi

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
            DOCKERMACHINE="docker run --runtime=nvidia"
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
    docker pull nicvicorob/mslesions:$DOCKER_VERSION
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
    eval $DOCKERMACHINE -ti  \
         -e DISPLAY=$DISPLAY \
         -u="docker" \
         -v /tmp/.X11-unix:/tmp/.X11-unix \
         -v $DATAPATH:/data:rw \
         -v $CURRENT_FOLDER/models:/home/docker/src/nets:rw \
         -v $CURRENT_FOLDER/config:/home/docker/src/config:rw \
         nicvicorob/mslesions:$DOCKER_VERSION  python -u app.py --docker | tee -a $CURRENT_FOLDER/logs/$DATE.txt
fi
