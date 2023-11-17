#!/usr/bin/env python3

########################################################################################
#
# Name: PCFG Merge Rules
#  --Probabilistic Context Free Grammar (PCFG) rule merger program
#
#  merge_rules.py
#
#########################################################################################

from __future__ import print_function
import sys
# Check for python3 and error out if not
if sys.version_info[0] < 3:
    print("This program requires Python 3.x", file=sys.stderr)
    sys.exit(1)
import argparse
import os
import configparser
import shutil
import json
import uuid

DEFAULT_ENCODING = 'utf8'


def _merge_file(file_a, file_b, output, weight, merge_encoding):
    # Read the first file and convert the structures to key value pairs
    file_a_dict = {}
    with open(file_a, encoding=merge_encoding) as fp_file_a:
        for line in fp_file_a:
            terminal, probability = line.rstrip().split('\t')
            file_a_dict[terminal] = float(probability)
    
    # Read the second file and convert the structures to key value pairs
    file_b_dict = {}
    with open(file_b, encoding=merge_encoding) as fp_file_b:
        for line in fp_file_b:
            terminal, probability = line.rstrip().split('\t')
            file_b_dict[terminal] = float(probability)
    output_dict = {}

    # Loop through all the structures in first file
    for terminal in file_a_dict.keys():
        # Check if the structure is present in the second file
        if terminal not in file_b_dict.keys():
            # If not present modify the propability by the weight
            output_dict[terminal] = (1 - weight) * file_a_dict[terminal]
        else:
            # If it is present involve the value of the probability in file2
            output_dict[terminal] = weight * file_b_dict[terminal] + (1 - weight) * file_a_dict[terminal]
    
    # Check if there are any elements which are not in file_b
    for terminal in file_b_dict.keys():
        if terminal not in file_a_dict.keys():
            output_dict[terminal] = weight * file_b_dict[terminal]

    # Reverse sort the dict so that the most likely value is first
    output_dict = {k: v for k, v in sorted(output_dict.items(), key=lambda item: item[1], reverse=True)}

    # Write the output keypair to the new file
    with open(output, 'w', encoding=merge_encoding) as fp_output:
        for terminal in output_dict.keys():
            fp_output.write(f'{terminal}\t{output_dict[terminal]:.20f}\n')


def _merge_files(generic_rule_dir, input_rule_dir, output_rule_dir, directory, generic_files, input_files, weight,
                 encoding):
    generic_dir = os.path.join(generic_rule_dir, directory)
    input_dir = os.path.join(input_rule_dir, directory)
    output_dir = os.path.join(output_rule_dir, directory)

    if os.path.exists(output_dir):
        return False
    else:
        os.mkdir(output_dir)
    
    for f in generic_files:
        # Loop through all the files from the generic dataset
        if f not in input_files:
            # If the file is found only in generic set, just copy the generic dataset
            shutil.copy(os.path.join(generic_dir, f), os.path.join(output_dir, f))
        else:
            # If the file is found also in the input file
            # We need to merge the files
            generic_file = os.path.join(generic_dir, f)
            input_file = os.path.join(input_dir, f)
            output_file = os.path.join(output_dir, f)
            _merge_file(generic_file, input_file, output_file, weight, encoding)
            
    for f in input_files:
        if f not in generic_files:
            # If a file is only found in the input rule set
            shutil.copy(os.path.join(input_dir, f), os.path.join(output_dir, f))
    return True


def merge_rules(generic_rule_dir, input_rule_dir, output_rule_dir, 
                weight, config_file_name = 'config.ini', replace_alphas_only = False):
    # Create the config objects
    generic_config = configparser.ConfigParser()
    with open(os.path.join(generic_rule_dir, config_file_name), encoding=DEFAULT_ENCODING) as fp:
        generic_config.read_file(fp)
    input_config = configparser.ConfigParser()
    with open(os.path.join(input_rule_dir, config_file_name), encoding=DEFAULT_ENCODING) as fp:
        input_config.read_file(fp)
    output_config = configparser.ConfigParser()
    
    for section in generic_config:
        # Loop through all the section in the generic config
        # Note, if the input contains more sections; those will not be added
        output_config[section] = generic_config[section]
        print(f'Merging {section}')

        if section == 'TRAINING_DATASET_DETAILS':
            # Replace some data from the input
            # Note that some values are still changed by some switches so
            # the data here might not always be correct
            merge_encoding = generic_config[section].get('encoding')
            if merge_encoding != input_config[section].get('encoding'):
                # Make sure to train with the same encodings
                raise RuntimeError('Encoding does not match between input and generic.')
            output_config[section]['comments'] = f'Merged {generic_config[section].get("uuid")} into {input_config[section].get("uuid")}.'
            output_config[section]['uuid'] = str(uuid.uuid4())
            output_config[section]['number_of_passwords_in_set'] = str(int(generic_config[section].get('number_of_passwords_in_set')) + int(input_config[section].get('number_of_passwords_in_set')))
            output_config[section]['number_of_encoding_errors'] = str(int(generic_config[section].get('number_of_encoding_errors')) + int(input_config[section].get('number_of_encoding_errors')))
            output_config[section]['filename'] = ''
        elif section in ['START', 'BASE_A', 'BASE_D', 'BASE_O', 'BASE_K', 'BASE_X', 'BASE_Y', 'BASE_Y', 'CAPITALIZATION']:
            generic_files = json.loads(generic_config[section].get('filenames'))
            input_files = json.loads(input_config[section].get('filenames'))
            directory = generic_config[section].get('directory')

            # If the replace_alphas_only switch is set, we will take the alphas structures
            # from the input dictionary, but keeping everything else from the generic dataset.
            if section == 'BASE_A' and replace_alphas_only is True:
                generic_files = []
            elif replace_alphas_only is True:
                input_files = []

            # Merging filenames variable in config
            output_config[section]['filenames'] = json.dumps(generic_files + input_files)
            # Merge content of files found in filenames variable
            _merge_files(generic_rule_dir, input_rule_dir, output_rule_dir, directory, generic_files, input_files,
                         weight, merge_encoding)

    with open(os.path.join(output_rule_dir, config_file_name), 'w', encoding=DEFAULT_ENCODING) as fp:
        output_config.write(fp)
    
    return generic_config, input_config, output_config


def parse_command_line(program_info):
    # Keeping the title text to be generic to make re-using code easier
    parser = argparse.ArgumentParser(
        description= program_info['name'] +
        ', version: ' + 
        program_info['version']
    )
        
    ## Standard options for filename, encoding, etc
    #
    # The rule name to save the grammar as. This will create a directory of
    # this name. Will also put associated other files, such as PRINCE wordlists
    # here.
    parser.add_argument(
        '--rule',
        '-r',
        help = 'Generic ruleset which will be used as a basis for the merge structure.',
        required = True,
    )

    parser.add_argument(
        '--input',
        '-i',
        help = 'Input ruleset which will be merged into the generic ruleset.',
        required = True,
    )

    parser.add_argument(
        '--output',
        '-o',
        help = 'The name of the output ruleset that will be created from merging the generic with the input ruleset.',
        required = True,
    )

    parser.add_argument(
        '--weight',
        '-w',
        help = 'Weight that will be given to the input ruleset when merging the rulesets.',
        required = True,
    )

    parser.add_argument(
        '--replace_alphas_only',
        help = 'Only merge the alpha structures from input. Keeping everything of generic rule set as is.',
        required = False,
        action='store_const',
        const= not program_info['replace_alphas_only'],
        default = program_info['replace_alphas_only']
    )

    args=parser.parse_args()

    # Standard Options
    program_info['rule'] = args.rule
    program_info['input'] = args.input
    program_info['output'] = args.output
    program_info['weight'] = float(args.weight)
    program_info['replace_alphas_only'] = args.replace_alphas_only

    return True


def main():
    # Information about this program
    program_info = {
    
        # Program and Contact Info
        'name':'PCFG Merge Rules',
        'version': '1.0',

        # Merge alphas only
        'replace_alphas_only': False,
    }

    print('PCFG Merge Rules')
    print("Version: " + str(program_info['version']))

    # Parsing the command line
    if not parse_command_line(program_info):
        # There was a problem with the command line so exit
        print("Exiting...")
        return

    weight = program_info['weight']
    replace_alphas_only = program_info['replace_alphas_only']

    base_directory = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'Rules',
                        )
    generic_rule_dir = os.path.join(base_directory, program_info['rule'])
    input_rule_dir = os.path.join(base_directory, program_info['input'])
    output_rule_dir = os.path.join(base_directory, program_info['output'])

    if os.path.exists(output_rule_dir):
        print(f'{output_rule_dir} already exists, exiting')
        return
    
    os.mkdir(output_rule_dir)

    if not merge_rules(generic_rule_dir, input_rule_dir, output_rule_dir, weight, replace_alphas_only = replace_alphas_only):
        print('Merging rules failed exiting')
        return
    
    # These sections are missing from the config.ini but still required.
    # Just copying from generic dataset for now
    for dir in ['Emails', 'Omen', 'Websites']:
        shutil.copytree(os.path.join(generic_rule_dir, dir), os.path.join(output_rule_dir, dir))


if __name__ == "__main__":
    main()
