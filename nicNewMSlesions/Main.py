# The Main file
# msalem@eia.udg.edu, mostafasalem@aun.edu.eg
# Mostafa Salem 2017
# to cite this work : 
# Mostafa Salem, Mariano Cabezas, Sergi Valverde, Deborah Pareto, Arnau Oliver, Joaquim Salvi, Alex Rovira,
#  Xavier Llado, A supervised framework with intensity subtraction and deformation field features for the
#  detection of new T2-w lesions in multiple sclerosis, In NeuroImage: Clinical, Volume 17, 2018,
#  Pages 607-615, ISSN 2213-1582, https://doi.org/10.1016/j.nicl.2017.11.015.
# (http://www.sciencedirect.com/science/article/pii/S2213158217302954)

from __future__ import print_function
import ConfigParser
import sys
import os
from subprocess import check_call


def color_codes():
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
    c = color_codes()
    # Display the option menus

    print(c['c'] + '\nWelcome....' + c['nc'])
    print(c['y'] + '\tChoose an option:' + c['nc'])
    print(c['g'] + '\t\t1- Train a model' + c['nc'])
    print(c['y'] + '\t\t2- Test a model' + c['nc'])
    print(c['g'] + '\t\t3- Test the old pipeline' + c['nc'])
    print(c['r'] + '\t\t4- Exit' + c['nc'])
    return int(raw_input(c['r'] + "\tYour choice:  " + c['nc']))


def parse_input(option):
    if option not in [1, 2, 3]:
        if option is not 4:
            print('Invalid option')
    else:
        dataset_path = raw_input("Enter the dataset full path: ")

        # Let's create that config file for next time...
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

        config_parser.write(config_file)
        config_file.close()

        docker_cmd = [
            'docker', 'run',
            '-v', '%s:/WorkingFiles/LR.conf' % os.path.realpath(config_name),
            '-v', '%s:/WorkingFiles/in/:rw' % dataset_path,
            '-it',
            'nicvicorob/newmslesions'
        ]
        check_call(docker_cmd)


def main():
    # Init
    option = None

    # Update docker
    with open(os.devnull, 'wb') as dev_null:
        check_call(
            'docker pull nicvicorob/newmslesions',
            stderr=dev_null,
            stdout=dev_null,
            shell=True
        )

    # Infinite loop
    while option is not 4:
        option = display_options_menu()
        parse_input(option)

    print('Bye bye....')

if __name__ == "__main__":
    main()
