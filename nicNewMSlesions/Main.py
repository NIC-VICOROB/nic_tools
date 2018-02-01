#!/usr/bin/python2.7
# The Main file
# msalem@atc.udg.edu, mostafasalem@aun.edu.eg, mcabezas@atc.udg.edu, mariano.cabezas@udg.edu
# Mostafa Salem & Mariano Cabezas (2018)
# to cite this work : 
# Mostafa Salem, Mariano Cabezas, Sergi Valverde, Deborah Pareto, Arnau Oliver, Joaquim Salvi, Alex Rovira,
#  Xavier Llado, A supervised framework with intensity subtraction and deformation field features for the
#  detection of new T2-w lesions in multiple sclerosis, In NeuroImage: Clinical, Volume 17, 2018,
#  Pages 607-615, ISSN 2213-1582, https://doi.org/10.1016/j.nicl.2017.11.015.
# (http://www.sciencedirect.com/science/article/pii/S2213158217302954)

from __future__ import print_function
import ConfigParser
import argparse
import sys
import os
from subprocess import check_call


def color_codes():
    """
    Utility function to encapsulate ASCII values to change the type color on the command prompt.
    :return: Dictionary with ASCII color values
    """
    codes = {
        'nc': '\033[0m',
        'b': '\033[1m',
        'k': '\033[0m',
        '0.25': '\033[30m',
        'dgy': '\033[30m',
        'r': '\033[31m',
        'g': '\033[32m',
        'gc': '\033[32m;0m',
        'bg': '\033[32;1m',
        'y': '\033[33m',
        'c': '\033[36m',
        '0.75': '\033[37m',
        'lgy': '\033[37m',
    }
    return codes


def display_options_menu():
    """
    Legacy menu to select the method to be run inside the docker container.
        Options 1 and 2 correspond to the logistic regression model, while option 3 corresponds to the
        old longitudinal pipeline.
        :return: The option chosen by the user
    """
    c = color_codes()
    # Display the option menus

    print(c['c'] + '\nWelcome....' + c['nc'])
    print(c['y'] + '\tChoose an option:' + c['nc'])
    print(c['g'] + '\t\t1- Train a model' + c['nc'])
    print(c['y'] + '\t\t2- Test a model' + c['nc'])
    print(c['g'] + '\t\t3- Test the old pipeline' + c['nc'])
    print(c['r'] + '\t\t4- Exit' + c['nc'])
    return int(raw_input(c['r'] + "\tYour choice:  " + c['nc']))


def parse_input(option, dataset_path):
    """
    Legacy menu to select the parameters for the docker container.
        This menu should be used to work with the logistic regression model. There is also the option
         to change the name of the Basal and 12M folders for the old pipeline.
        After introducing the parameters, the docker is called.
    """
    if option not in ['old', 'new', 1, 2, 3]:
        if option is not 4:
            print('Invalid option')
    else:
        # Let's create that config file for next time...
        if option not in ['old', 'new']:
            config_name = './config/LR.conf'
            config_file = open(config_name, 'w')
            config_parser = ConfigParser.ConfigParser()

            '''Add the settings to the structure parser of the file, and let's write it out...'''
            # - Action = the operation required to be run in the docker
            actions = ['train', 'test', 'old']
            config_parser.add_section('action')
            config_parser.set('action', 'action_num', actions[option - 1])

            # - General parameters
            config_parser.add_section('general')
            # The segmentation method only affects preprocessing
            # All the options not related to evaluation need to define which is the baseline and follow-up folders
            config_parser.set(
                'general',
                'base_folder_name',
                raw_input("Enter the Baseline folder name (empty for Basal): ") or 'Basal'
            )
            config_parser.set(
                'general',
                'followup_folder_name',
                (raw_input("Enter the followup folder name (empty for 12M): ") or '12M')
            )
            print("Number of modalities: (2 = PD and FLAIR), (3 = T2, PD, and FLAIR), (4 = T1, T2, PD, and FLAIR)")
            config_parser.set(
                'general',
                'num_modality',
                (raw_input("Enter the num of modality to work with (empty for 4): ") or '4')
            )
            # All the training options, and the evaluation one use the GT images
            if option is 1:
                config_parser.set(
                    'general',
                    'gt_name',
                    (raw_input("Enter the ground truth file name (empty for lesionMask.nii): ") or 'lesionMask.nii')
                )

            # - Preprocessing options
            config_parser.add_section('preprocessing')
            config_parser.set(
                'preprocessing',
                'wm_seg_method',
                (raw_input("Enter WM segmentation method (empty for 0): ") or '0')
            )

            # - Training the model with the whole dataset
            config_parser.add_section('model')
            config_parser.set(
                'model',
                'lr_model',
                raw_input("Enter the name for the LR model's file (LRModel.h5 file): " or 'LRModel.h5')
            )

        elif option is 'old':
            config_name = './config/old.conf'
            config_file = open(config_name, 'w')
            config_parser = ConfigParser.ConfigParser()
            config_parser.add_section('action')
            config_parser.set('action', 'action_num', 'old')
            config_parser.add_section('general')
            config_parser.set('general', 'num_modality', 4)
            config_parser.set('general', 'base_folder_name', 'time1')
            config_parser.set('general', 'followup_folder_name', 'time2')
            config_parser.set('general', 'gt_name', '')
            config_parser.add_section('preprocessing')
            config_parser.set('preprocessing', 'wm_seg_method', '0')
            config_parser.add_section('model')
            config_parser.set('model', 'lr_model', '')
        else:
            config_name = './config/new.conf'
            config_file = open(config_name, 'w')
            config_parser = ConfigParser.ConfigParser()
            config_parser.add_section('action')
            config_parser.set('action', 'action_num', 'test')
            config_parser.add_section('general')
            config_parser.set('general', 'num_modality', 4)
            config_parser.set('general', 'base_folder_name', 'time1')
            config_parser.set('general', 'followup_folder_name', 'time2')
            config_parser.set('general', 'gt_name', '')
            config_parser.add_section('preprocessing')
            config_parser.set('preprocessing', 'wm_seg_method', '0')
            config_parser.add_section('model')
            config_parser.set('model', 'lr_model', 'LRModel.h5')

        config_parser.write(config_file)
        config_file.close()

        # Global command that works for --devel and normal
        docker_cmd = [
            'docker', 'run',
            '-v', '%s:/home/docker/LR.conf' % os.path.realpath(config_name),
            '-v', '%s:/home/docker/in/:rw' % dataset_path,
            '-v', '%s:/home/docker/models:rw' % os.path.realpath('models'),
            '-it',
            'nicvicorob/newmslesions'
        ]
        check_call(docker_cmd)


def parse_args():
    """
    Function to control the arguments of the python script when called from the command line.
        If no argument is given, we assume a default mode where the user only wants to process
        with the old pipeline. Otherwise the --devel flag should be used. This flag allows to use
        the legacy display menu from Mostafa Salem with the limited number of options for:
        Training, testing and old pipeline.
        :return: Dictionary with the argument values
    """
    parser = argparse.ArgumentParser(description='Run the longitudinal MS lesion segmentation docker.')
    parser.add_argument(
        '-f', '--folder',
        dest='data_path', default='/data/longitudinal/',
        help='Folder where the dataset is stored'
    )
    parser.add_argument(
        '-n', '--new',
        dest='new', action='store_true', default=False,
        help='Option to run the new pipeline without menu prompts'
    )
    parser.add_argument(
        '-d', '--devel',
        dest='devel', action='store_true', default=False,
        help='Developer option with legacy menu'
    )
    return vars(parser.parse_args())


def main():
    """
    Main function
    """
    # Update docker
    print('Checking for updates...', end=' ')
    with open(os.devnull, 'wb') as dev_null:
        check_call(
            'docker pull nicvicorob/newmslesions',
            stderr=dev_null,
            stdout=dev_null,
            shell=True
        )
    print('Done')

    # Argument parsing. If the devel option is used we use the legacy menu. Otherwise just run a simplified
    # version based on the old pipeline.
    options = parse_args()
    if options['devel']:
        option = None

        # Infinite loop
        while option is not 4:
            option = display_options_menu()
            parse_input(option, options['data_path'])

        print('Bye bye....')
    else:
        parse_input('old', options['data_path'])

if __name__ == "__main__":
    main()
