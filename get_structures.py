#!/usr/bin/env python3

########################################################################################
#
# Name: get_structures
#  --Want to get words from a rule set? Then this is the tool for you!
#  --Easy wordlist builder from Rule set
#
#  get_structures.py
#
#########################################################################################

import argparse
import os
import sys

def parse_command_line(program_info):
    # Keeping the title text to be generic to make re-using code easier
    parser = argparse.ArgumentParser(
        description= program_info['name'] +
        ', version: ' + 
        program_info['version']
    )

    parser.add_argument(
        '--rule',
        '-r',
        help = 'Input rule, from which to get.',
        required = True,
    )
    parser.add_argument(
        '--alpha',
        '-a',
        help = 'Only get the Alphas, like words.',
        action = 'store_true',
        required = False,
        default = False
    )
    
    parser.add_argument(
        '--min_length',
        help = 'If used, checks for the minimal length of grammars.',
        type=int,
        default = 0,
    )

    parser.add_argument(
        '--max_length',
        help = 'If used, checks for the minimal length of grammars.',
        type=int,
        default = 40,
    )
    parser.add_argument(
        '--rules_dir',
        '-D',
        help = 'Path to the Rules folder',
        required = False,
        action='store',
        default = os.path.join('..', 'pcfg_cracker', 'Rules')
    )

    args=parser.parse_args()
    program_info['alpha'] = args.alpha
    program_info['rule'] = args.rule
    program_info['rules_dir'] = args.rules_dir
    program_info['max_length'] = args.max_length
    program_info['min_length'] = args.min_length
    
    return True

def main():
    program_info = {
        # Program and Contact Info
        'name': 'PCFG Get Structures',
        'version': '1.0',
    }
    print('PCFG Get Structures', file=sys.stderr)
    print("Version: " + str(program_info['version']), file=sys.stderr)

    # Parsing the command line
    if not parse_command_line(program_info):
        # There was a problem with the command line so exit
        print("Exiting...")
        return

    if program_info['alpha']:
        for n in range(program_info['min_length'], program_info['max_length'] + 1):
            n = f"{n}.txt"
            path = os.path.join(program_info['rules_dir'], program_info['rule'], 'Alpha', n)
            if os.path.isfile(path):
                with open(os.path.join(program_info['rules_dir'], program_info['rule'], 'Alpha', n)) as f:
                    for line in f.readlines():
                        line = line.rstrip('\n')
                        line = line.split('\t')[0]
                        print(line)

if __name__ == "__main__":
    main()
