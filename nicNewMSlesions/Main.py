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


def parse_input(option, dataset_path, options):
    """
    Function that prepares a config file for the docker. It also selects the container where everything will be run.
    Right now, we have this option to work with both a production image for the hospitals, and a developer image to
    test the algorithms before pushing them to production.
    :param option: String that represents the option we'll be running on the docker container.
    :param dataset_path: Path for the dataset that will be mounted on the container.
    :return: None.
    """
    path = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    if not os.path.isdir(os.path.join(path, 'config')):
        os.mkdir(os.path.join(path, 'config'))
    # Let's create that config file for next time...
    baseline_folder = options['time1']
    followup_folder = options['time2']
    if option is 'old' or option is 'new':
        config_name = os.path.join(path, 'config', 'old.conf')
        action = 'old'
    elif option is 'gui':
        config_name = os.path.join(path, 'config', 'gui.conf')
        action = option
    else:
        config_name = os.path.join(path, 'config', 'lr.conf')
        action = option

    config_file = open(config_name, 'w')
    config_parser = ConfigParser.ConfigParser()
    config_parser.add_section('action')
    config_parser.set('action', 'action', action)
    config_parser.add_section('general')
    if option is 'old':
        config_parser.add_section('preprocessing')
        config_parser.set('preprocessing', 'wm_seg_method', 0)
    config_parser.set('general', 'num_modality', 4)
    config_parser.set('general', 'base_folder_name', baseline_folder)
    config_parser.set('general', 'followup_folder_name', followup_folder)
    config_parser.set('general', 'gt_name', 'lesionMask.nii')
    config_parser.add_section('model')
    config_parser.set('model', 'lr_model', 'LRModel.h5')

    config_parser.write(config_file)
    config_file.close()

    # Global command that works for any input
    if option is 'old':
        docker_image = 'nicvicorob/newmslesions:latest'
    else:
        docker_image = 'nicvicorob/newmslesions:devel'

    docker_cmd = [
        'docker', 'run',
        '-u' if options['user'] is not None else '',
        options['user'] if options['user'] is not None else '',
        '-e', 'DISPLAY=%s' % os.environ['DISPLAY'] if 'DISPLAY' in os.environ.keys() else ':0',
        '-v', '/tmp/.X11-unix:/tmp/.X11-unix',
        '-v', '%s:/home/docker/LR.conf' % config_name,
        '-v', '%s:/home/docker/in/:rw' % dataset_path,
        '-v', '%s:/home/docker/models:rw' % os.path.join(path, 'models'),
        '-it',
        docker_image
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-f', '--old',
        dest='old_path', default='/data/longitudinal/',
        help='Option to use the old pipeline in the production docker. The second parameter should be the folder where'
             'the patients are stored.'
    )
    group.add_argument(
        '-d', '--devel',
        dest='new_path', default=None,
        help='Option to use the old pipeline in the development docker. The second parameter should be the folder where'
             'the patients are stored.'
    )
    group.add_argument(
        '-t', '--train',
        dest='train_path', default=None,
        help='Option to train the logistic regression model. The second parameter should be the folder where'
             'the patients are stored.'
    )
    group.add_argument(
        '-T', '--test',
        dest='test_path', default=None,
        help='Option to test a logistic regression model. The second parameter should be the folder where'
             'the patients are stored.'
    )
    group.add_argument(
        '-l', '--leave-one-out',
        dest='loo_path', default=None,
        help='Option to use the logistic regression model with leave-one-out cross-validation. The second parameter'
             ' should be the folder where the patients are stored.'
    )
    group.add_argument(
        '-g', '--gui',
        dest='gui_path', default=None,
        help='Option to use a gui to setup parameters for segmentation and select the method. The second parameter'
             ' should be the folder where the patients are stored.'
    )
    parser.add_argument(
        '-B', '--time1',
        dest='time1', default='time1',
        help='Name of the baseline folder'
    )
    parser.add_argument(
        '-F', '--time2',
        dest='time2', default='time2',
        help='Name of the followup folder'
    )
    parser.add_argument(
        '-u', '--user',
        dest='user', default=None,
        help='Name of the followup folder'
    )
    return vars(parser.parse_args())


def main():
    """
    Main function
    """
    # Update docker
    print('Checking for updates...', end=' ')
    sys.stdout.flush()
    with open(os.devnull, 'wb') as dev_null:
        check_call(
            'docker pull nicvicorob/newmslesions:devel',
            stderr=dev_null,
            stdout=dev_null,
            shell=True
        )
        check_call(
            'docker pull nicvicorob/newmslesions:latest',
            stderr=dev_null,
            stdout=dev_null,
            shell=True
        )
    print('Done')

    # Argument parsing. If the devel option is used we use the legacy menu. Otherwise just run a simplified
    # version based on the old pipeline.
    options = parse_args()
    if options['new_path'] is not None:
        parse_input('new', options['new_path'], options)
    elif options['train_path'] is not None:
        parse_input('train', options['train_path'], options)
    elif options['test_path'] is not None:
        parse_input('test', options['test_path'], options)
    elif options['loo_path'] is not None:
        parse_input('loo', options['loo_path'], options)
    elif options['gui_path'] is not None:
        parse_input('gui', options['gui_path'], options)
    elif options['old_path'] is not None:
        parse_input('old', options['old_path'], options)
        raw_input('Press enter to finish\n')


if __name__ == "__main__":
    main()
