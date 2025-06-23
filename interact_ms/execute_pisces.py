""" Functions for executing PISCES within inSPIRE-interactive.
"""
import ast
import os
import shutil
import sys
import time

import yaml

from interact_ms.constants import (
    CONTAM_FOLDER_KEY,
    CPUS_KEY,
    EXTRA_PROT_KEY,
    INTERACT_HOME_KEY,
    MHCPAN_KEY,
    RESCORE_COMMAND_KEY,
    SKYLINE_RUNNER_KEY,
    SLURM_SCRIPT_KEY,
)
from interact_ms.utils import (
    check_pids, write_task_status, subset_tasks,
)
from interact_ms.pisces_script import PISCES_SCRIPT

USE_CASES = {
    'noncan': 'nonCanonicalDiscovery',
    'assembly': 'proteomeAssembly'
}

def execute_pisces(app_config, project_home, config_dict, tasks=None):
    """ Function to execute PISCES, writes config file, a python script with all
        required tasks, and then executes the python script in the background.
    """
    pisces_settings = prepare_pisces(config_dict, project_home, app_config)
    write_task_status(pisces_settings, project_home, tasks)
    task_list = subset_tasks(pisces_settings, tasks=tasks, mode='pisces')

    # In case of rerunning, we should be careful not to reuse this file.
    if (
        'canonical' in task_list and 
        os.path.exists(f'{project_home}/outputFolder/canonicalOutput/formated_df.csv')
    ):
        os.remove(f'{project_home}/outputFolder/canonicalOutput/formated_df.csv')

    pisces_script = PISCES_SCRIPT.format(
        home_key=app_config[INTERACT_HOME_KEY],
        project_home=project_home,
        task_list=','.join(task_list)
    )
    script_path = f'{project_home}/pisces_script.py'
    with open(script_path, mode='w', encoding='UTF-8') as script_file:
        script_file.writelines(pisces_script)

    os.popen(
        f'{sys.executable} {script_path} > {project_home}/execution_log.txt 2>&1'
    )
    for idx in range(3):
        if check_pids(project_home) == 'waiting':
            break

        time.sleep(idx+1)

def prepare_pisces(config_dict, project_home, app_config):
    """ Function to prepare the PISCES run.
    """
    pisces_settings = {'variant': 'pisces'}
    pisces_settings['quantify'] = bool(config_dict['runQuantification'])


    if (
        os.path.exists(f'{project_home}/search/dbSearch.csv') or
        os.path.exists(f'{project_home}/search/dbSearch_0.csv')
    ):
        db_search_result = [f'{project_home}/search/dbSearch*.csv']
    else:
        db_search_result = None


    output_config = {
        'experimentTitle': config_dict['project'],
        'dbSearchResults': db_search_result,
        'scansFolder': f'{project_home}/ms',
        'scansFormat': 'mgf',
        'outputFolder': f'{project_home}/outputFolder',
        'mzAccuracy': float(config_dict['mzAccuracy']),
        'mzUnits': config_dict['mzUnits'],
        'nCores': app_config[CPUS_KEY],
        SLURM_SCRIPT_KEY: app_config[SLURM_SCRIPT_KEY],
        CONTAM_FOLDER_KEY: app_config[CONTAM_FOLDER_KEY],
        'additionalConfigs': {
            'skylineRunner': app_config[SKYLINE_RUNNER_KEY],
            RESCORE_COMMAND_KEY: app_config[RESCORE_COMMAND_KEY],
        }
    }
    if config_dict['datasetType'] == 'tryp':
        output_config['enzyme'] = 'trypsin'
    
    with open(f'{project_home}/search_metadata.yml', 'r', encoding='UTF-8') as stream:
        db_search_config = yaml.safe_load(stream)
        output_config['dbSearchEngine'] = db_search_config['searchEngine']
        output_config['runDbSearch'] = bool(db_search_config['runFragger'])

    with open(f'{project_home}/denovo_metadata.yml', 'r', encoding='UTF-8') as stream:
        dn_config = yaml.safe_load(stream)
        if dn_config['runCasa'] == 1:
            pisces_settings['runCasa'] = True
            output_config['casaSingImg'] = app_config['casaSingImg']
            output_config['casaModel'] = app_config['casaModel']
        output_config['deNovoMethod'] = dn_config['deNovoEngine']
        if output_config['deNovoMethod'] == 'casanovo':
            if dn_config['runCasa'] == 1:
                output_config['deNovoResults'] = [f'{project_home}/ms/*.mztab']
            else:
                output_config['deNovoResults'] = [f'{project_home}/search/*.mztab']
        else:
            output_config['deNovoResults'] = [f'{project_home}/search/deNovo*.csv']

    if config_dict['piscesSelection'] == 'none':
        raise ValueError('You must select your PISCES use case.')
    output_config['useCase'] = USE_CASES[config_dict['piscesSelection']]

    if output_config['useCase'] == 'nonCanonicalDiscovery':
        if config_dict['crypticFolder'] == 'no cryptic database used':
            config_dict['crypticFolder'] = None
        output_config[EXTRA_PROT_KEY] = config_dict['crypticFolder']
    else:
        output_config['fraggerMemory'] = app_config['fraggerMemory']
        output_config['fraggerPath'] = app_config['fraggerPath']


    if 'useBindingAffinity' in config_dict:
        output_config['useBindingAffinity'] = config_dict['useBindingAffinity']
        output_config['alleles'] = [
            elem.strip() for elem in  config_dict["alleles"].split(",")
        ]
        output_config['netMHCpan'] = app_config[MHCPAN_KEY]
        pisces_settings['binding'] = True
    else:
        pisces_settings['binding'] = False

    if os.path.exists(f'{project_home}/proteome'):
        proteome_files = os.listdir(f'{project_home}/proteome')
        if len(proteome_files) > 0:
            prot_file_name = proteome_files[0]
            if output_config['useCase'] == 'proteomeAssembly':
                output_config['genome'] = f'{project_home}/proteome/{prot_file_name}'
            else:
                output_config['proteome'] = f'{project_home}/proteome/{prot_file_name}'
        else:
            raise ValueError('No proteome file uploaded.')

    for config_key, config_value in config_dict['additionalConfigs'].items():
        try:
            output_config[config_key] = ast.literal_eval(config_value)
        except ValueError:
            output_config[config_key] = config_value

    with open(f'{project_home}/config.yml', 'w', encoding='UTF-8') as yaml_out:
        yaml.dump(output_config, yaml_out)

    return pisces_settings
