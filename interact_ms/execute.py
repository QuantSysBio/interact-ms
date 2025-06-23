""" Functions for executing jobs (inSPIRE, PEPSeek, etc.) within interact-ms.
"""
import ast
import os
import sys
import time

from inspire.config import ALL_CONFIG_KEYS
import yaml

from interact_ms.constants import (
    CPUS_KEY,
    FRAGGER_MEMORY_KEY,
    FRAGGER_PATH_KEY,
    INTERACT_HOME_KEY,
    MHCPAN_KEY,
    RESCORE_COMMAND_KEY,
    SKYLINE_RUNNER_KEY,
)
from interact_ms.utils import (
    check_pids, write_task_status, read_meta, subset_tasks,
)
from interact_ms.inspire_script import INSPIRE_SCRIPT
from interact_ms.inspire_invitro_script import INSPIRE_INVITRO_SCRIPT

def execute_invitro_job(app_config, project_home, config_dict, tasks=None):
    """ Function to execute job, writes config file, a bash file with all
        required tasks, and then executes the bash file in the background.
    """
    # print('los')
    # os.system(
    #     f'mkdir -p {project_home}/outputFolder && cp -rp /data/John/interact-1.1/inspire_invitro {project_home}/outputFolder'
    # )
    job_settings = prepare_invitro_inspire(config_dict, project_home, app_config)
    write_task_status(job_settings, project_home, tasks)

    task_list = subset_tasks(job_settings, tasks, 'invitro')
    print(task_list)
    inspire_script = INSPIRE_INVITRO_SCRIPT.format(
        home_key=app_config[INTERACT_HOME_KEY],
        project_home=project_home,
        task_list=','.join(task_list),
        apptainer_image=app_config['apptainerImage'],
        spliced_upper_limit=job_settings['splicedUpperLimit'],
    )
    script_path = f'{project_home}/inspire_script.py'
    with open(script_path, mode='w', encoding='UTF-8') as script_file:
        script_file.writelines(inspire_script)

    os.popen(
        f'{sys.executable} {script_path} > {project_home}/execution_log.txt 2>&1'
    )
    for idx in range(3):
        if check_pids(project_home) == 'waiting':
            break

        time.sleep(idx+1)

def execute_job(app_config, project_home, config_dict, tasks=None):
    """ Function to execute job, writes config file, a bash file with all
        required tasks, and then executes the bash file in the background.
    """
    job_settings = prepare_inspire(config_dict, project_home, app_config)
    write_task_status(job_settings, project_home, tasks)

    # In case of rerunning, we should be careful not to reuse this file.
    if os.path.exists(f'{project_home}/outputFolder/formated_df.csv'):
        os.remove(f'{project_home}/outputFolder/formated_df.csv')

    task_list = subset_tasks(job_settings, tasks)
    inspire_script = INSPIRE_SCRIPT.format(
        home_key=app_config[INTERACT_HOME_KEY],
        project_home=project_home,
        task_list=','.join(task_list)
    )
    script_path = f'{project_home}/inspire_script.py'
    with open(script_path, mode='w', encoding='UTF-8') as script_file:
        script_file.writelines(inspire_script)

    os.popen(
        f'{sys.executable} {script_path} > {project_home}/execution_log.txt 2>&1'
    )
    for idx in range(3):
        if check_pids(project_home) == 'waiting':
            break

        time.sleep(idx+1)

def prepare_invitro_inspire(config_dict, project_home, app_config):
    """ Function to prepare the inSPIRE run.
    """
    fragger_config = {
        'baseDir': project_home,
        'folder': f'{project_home}/ms',
        'ms1_accuracy': float(config_dict['ms1Accuracy']),
        'ms2_accuracy': float(config_dict['mzAccuracy']),
        'ms2_units': config_dict['mzUnits'],
        'contaminantsDatabase': f'{project_home}/proteome-invitro/contams.fasta',
        'substrateSequence': f'{project_home}/proteome-invitro/protSeq.fasta',
        'splicedDatabase': f'{project_home}/proteome-invitro/allPSP.fasta',
        'nTopCandidates': 20,
        'nSplits': 50,
        'fraggerMemory': app_config['fraggerMemory'],
        'fraggerPath': app_config['fraggerPath'],
    }
    with open(f'{project_home}/config_fragger.yml', 'w', encoding='UTF-8') as yaml_out:
        yaml.dump(fragger_config, yaml_out)

    inspire_config = {
        'accessionFormat': 'invitroSPI',
        'dropUnknownPTMs': True,
        'experimentTitle': project_home.split('/')[-1],
        'mzAccuracy': float(config_dict['mzAccuracy']),
        'mzUnits': config_dict['mzUnits'],
        'outputFolder': '/mnt/outputFolder',
        'proteome': '/mnt/proteome-invitro/protSeq.fasta',
        'reduce': 'no',
        'rescoreMethod': 'percolatorSeparate',
        'deltaMethod': 'ignore',
        'reuseInput': True,
        'scansFolder': '/mnt/ms',
        'scansFormat': 'mgf',
        'searchEngine': 'msfragger',
        'searchResults': [
            '/mnt/ms/cleaved/*.pepXML',
            '/mnt/ms/spliced/*.pepXML',
        ],
        'silentExecution': True,
        'useAccessionStrata': True,
        'useMinimalFeatures': True,
        'nCores': 5,
        'includeFeatures':[
            'spectralAngle', 'deltaRT', 'spearmanR',
        ],
        'resultsExport': 'peptide',
    }
    with open(f'{project_home}/config.yml', 'w', encoding='UTF-8') as yaml_out:
        yaml.dump(inspire_config, yaml_out)

    contams_config = {
        'deltaMethod': 'ignore',
        'dropUnknownPTMs': True,
        'experimentTitle': f'{project_home.split("/")[-1]}_contams',
        'mzAccuracy': float(config_dict['mzAccuracy']),
        'mzUnits': config_dict['mzUnits'],
        'outputFolder': '/mnt/contamsOutputFolder',
        'reduce': 'no',
        'rescoreMethod': 'percolatorSeparate',
        'reuseInput': True,
        'scansFolder': '/mnt/ms',
        'scansFormat': 'mgf',
        'searchEngine': 'msfragger',
        'searchResults': [
            '/mnt/ms/contams/*.pepXML',
        ],
        'silentExecution': True,
        'useMinimalFeatures': True,
        'nCores': 5,
    }
    with open(f'{project_home}/config_contam.yml', 'w', encoding='UTF-8') as yaml_out:
        yaml.dump(contams_config, yaml_out)

    return {'variant': 'invitro', 'splicedUpperLimit': int(config_dict['splicedUpperLimit'])}

def prepare_inspire(config_dict, project_home, app_config):
    """ Function to prepare the inSPIRE run.
    """
    inspire_settings = {
        'fragger': False,
        'pathogen': False,
    }

    inspire_settings['quantify'] = bool(config_dict['runQuantification'])
    if inspire_settings['quantify']:
        inspire_settings['skylinePrecursorCountFilter'] = int(config_dict['quantPrecCount'])
        inspire_settings['skylineIdpCutOff'] = float(config_dict['quantIdp'])

    output_config = {
        'experimentTitle': config_dict['project'],
        'scansFormat': 'mgf',
        'outputFolder': f'{project_home}/outputFolder',
        'mzAccuracy': float(config_dict['mzAccuracy']),
        'ms1Accuracy': float(config_dict['ms1Accuracy']),
        'mzUnits': config_dict['mzUnits'],
        'silentExecution': True,
        'reuseInput': True,
        'fraggerPath': app_config[FRAGGER_PATH_KEY],
        'fraggerMemory': app_config[FRAGGER_MEMORY_KEY],
        'nCores': app_config[CPUS_KEY],
        'skylineRunner': app_config[SKYLINE_RUNNER_KEY],
        RESCORE_COMMAND_KEY: app_config[RESCORE_COMMAND_KEY],
        'technicalReplicates': config_dict['technicalReplicates'],
    }

    if config_dict['datasetType'] == 'tryp':
        output_config['enzyme'] = 'trypsin'

    meta_dict = read_meta(project_home, 'search')
    if not meta_dict:
        raise ValueError('No Search Engine information was provided.')

    output_config['searchEngine'] = meta_dict.get('searchEngine', 'msfragger')
    inspire_settings['fragger'] = bool(meta_dict.get('runFragger', 1))
    if inspire_settings['fragger']:
        if meta_dict['fraggerUseContams'] == 'yes':
            output_config['fraggerUseContams'] = True
        else:
            output_config['fraggerUseContams'] = False

    if 'useBindingAffinity' in config_dict:
        output_config['useBindingAffinity'] = config_dict['useBindingAffinity']
        output_config['alleles'] = [
            elem.strip() for elem in  config_dict["alleles"].split(",")
        ]
        output_config['netMHCpan'] = app_config[MHCPAN_KEY]
        inspire_settings['binding'] = True
    else:
        inspire_settings['binding'] = False

    if not inspire_settings['fragger']:
        output_config['searchResults'] = [
            f'{project_home}/search/{filename}' for filename in os.listdir(
                f'{project_home}/search/'
            )
        ]

    if 'epitopeCutLevel' in config_dict:
        output_config['epitopeCutLevel'] = config_dict['epitopeCutLevel']

    output_config['scansFolder'] = f'{project_home}/ms'

    if output_config['searchEngine'] in ('mascot', 'msfragger'):
        output_config['rescoreMethod'] = 'percolatorSeparate'
    else:
        output_config['rescoreMethod'] = 'percolator'

    if os.path.exists(f'{project_home}/search/fragger_params.template'):
        output_config['fraggerParams'] = f'{project_home}/search/fragger_params.template'

    if os.path.exists(f'{project_home}/proteome'):
        proteome_files = os.listdir(f'{project_home}/proteome')
        if len(proteome_files) > 0:
            prot_file_name = proteome_files[0]
            output_config['proteome'] = f'{project_home}/proteome/{prot_file_name}'
            output_config['inferProteins'] = True
    else:
        proteome_files = os.listdir(f'{project_home}/proteome-select')
        if len(proteome_files) < 2:
            raise ValueError('For inSPIRE-Pathogen, proteome files must be uploaded.')
        inspire_settings['pathogen'] = True
        output_config['proteome'] = f'{project_home}/proteome-select/proteome_combined.fasta'
        path_name = [
            prot_file for prot_file in proteome_files if prot_file.startswith('pathogen_')
        ][0]
        host_name = [
            prot_file for prot_file in proteome_files if prot_file.startswith('host_')
        ][0]
        output_config['pathogenProteome'] = f'{project_home}/proteome-select/{path_name}'
        output_config['hostProteome'] = f'{project_home}/proteome-select/{host_name}'
        output_config['controlFlags'] = [
            elem.strip() for elem in config_dict["controlFlags"].split(",") if elem
        ]
        output_config['inferProteins'] = True

    for config_key, config_value in config_dict['additionalConfigs'].items():
        if config_key not in ALL_CONFIG_KEYS:
            raise ValueError(f'Error {config_key} is not a valid inSPIRE config.')
        try:
            output_config[config_key] = ast.literal_eval(config_value)
        except:
            output_config[config_key] = config_value


    with open(f'{project_home}/config.yml', 'w', encoding='UTF-8') as yaml_out:
        yaml.dump(output_config, yaml_out)

    return inspire_settings
