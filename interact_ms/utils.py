""" Utility functions for interact-ms.
"""
from copy import deepcopy
import os
import subprocess
import time

import pandas as pd
import psutil
import yaml

from interact_ms.constants import (
    INTERACT_HOME_KEY,
    INVITRO_TASKS,
    INVITRO_TASK_DESCRIPTIONS,
    PISCES_TASK_DESCRIPTIONS,
    PISCES_TASK_NAMES,
    SERVER_ADDRESS_KEY,
    TASKS_NAMES,
    TASK_DESCRIPTIONS,
)
from interact_ms.html_snippets import (
    INTERACT_FOOTER,
    INTERACT_HEADER,
)

def get_task_list(user, project, app, variant):

    home_key= app.config[INTERACT_HOME_KEY]
    project_home = f'{home_key}/projects/{user}/{project}'

    if variant == 'invitro':
        return INVITRO_TASKS
    elif variant == 'pisces':
        tasks = deepcopy(PISCES_TASK_NAMES)
        dn_config = read_meta(project_home, 'denovo')
    else:
        tasks = deepcopy(TASKS_NAMES)

    params_config = read_meta(project_home, 'parameters')
    search_config = read_meta(project_home, 'search')

    if variant == 'pisces':
        if not dn_config.get('runCasa', False):
            tasks = [task for task in tasks if task != 'runCasa']
        
        if params_config.get('piscesSelection') != 'assembly':
            tasks = [task for task in tasks if task != 'translateGenome']
    if params_config.get('useBindingAffinity') not in ['asValidation', 'asFeature']:
        tasks = [task for task in tasks if task != 'predictBinding']
    if variant != 'pathogen':
        tasks = [task for task in tasks if task != 'extractCandidates']
    if not params_config['runQuantification']:
        tasks = [task for task in tasks if task != 'quantify']

    return tasks

def generate_subset_table(user, project, app, variant):
    """ Function to create a html table with raw file, biological sample input
        and (if required) checkbox for file is infected or not
    """
    html_table = '''
        <tr align="center" valign="center">
            <td><b>Task</b></td>
            <td><b>Task Description</b></td>
            <td><b>Run Task</b></td>
        </tr>
    '''
    tasks = get_task_list(user, project, app, variant)
    if variant == 'invitro':
        descriptions = INVITRO_TASK_DESCRIPTIONS
    elif variant == 'pisces':
        descriptions = PISCES_TASK_DESCRIPTIONS
    else:
        descriptions = TASK_DESCRIPTIONS
    for task in tasks:
        html_table += f'''
            <tr align="center" valign="center" text-align="left">
            <td>{task}</td>
			<td>{descriptions[task]}</td>
            <td>
                <input type="checkbox" class="infection-checkbox" style="align: center" id="{task}_included" name="{task}_included">
            </td>
        '''
        html_table += '</tr>'

    return html_table

def generate_raw_file_table(user, project, app, variant):
    """ Function to create a html table with raw file, biological sample input
        and (if required) checkbox for file is infected or not
    """
    home_key= app.config[INTERACT_HOME_KEY]
    project_home = f'{home_key}/projects/{user}/{project}'

    if variant == 'pathogen':
        html_table = '''
            <tr align="center" valign="center">
                <td><b>Raw File</b></td>
                <td><b>Biological Sample</b></td>
                <td><b>Infected Sample</b></td>
            </tr>
        '''
    else:
        html_table = '''
            <tr align="center" valign="center">
                <td><b>Raw File</b></td>
                <td><b>Biological Sample</b></td>
            </tr>
        '''

    sample_files = sorted(list({
        file_name[:-4] for file_name in os.listdir(
            f'{project_home}/ms'
        ) if (
            file_name.lower().endswith('.raw') or
            file_name.lower().endswith('.mgf')
        )
    }))

    for sample_idx, sample_name in enumerate(sample_files):
        html_table += f'''
            <tr align="center" valign="center">
            <td>{sample_name}</td>
			<td>
                <input type="text" class="sample-value" value="{sample_idx+1}"
                    onkeypress="textSubmit(event, '{app.config[SERVER_ADDRESS_KEY]}', 'noAction')"/>
            </td>
        '''
        if variant == 'pathogen':
            html_table += f'''
                <td>
					<input type="checkbox" class="infection-checkbox" style="align: center" id="{sample_name}_infected" name="{sample_name}_infected">
				</td>
            '''
        html_table += '</tr>'

    return html_table


def safe_job_id_fetch(project_home, running_via_slurm=False):
    """ Fetch the job ID of a job if it exists.
    """
    # if running_via_slurm:
    #     file_name = 'slurm_ids.txt'
    # else:
    #     file_name = 'job_pids.txt'
    file_name = 'job_pids.txt'

    if not os.path.exists(f'{project_home}/{file_name}'):
        time.sleep(2)

    if os.path.exists(f'{project_home}/{file_name}'):
        with open(f'{project_home}/{file_name}', 'r', encoding='UTF-8') as pid_file:
            return int(pid_file.readline().strip())
    return 0

def get_pids(project_home, running_via_slurm=False):
    """ Function to get the pids
    """
    if running_via_slurm:
        file_name = 'slurm_ids.txt'
    else:
        file_name = 'job_pids.txt'
    if not os.path.exists(f'{project_home}/{file_name}'):
        time.sleep(3)
        if not os.path.exists(f'{project_home}/{file_name}'):
            return None

    with open(f'{project_home}/{file_name}', 'r', encoding='UTF-8') as file:
        lines = file.readlines()
        pids = [line.rstrip() for line in lines]
        pids = [pid.strip() for pid in pids]

        if not pids:
            return None
    return pids


def read_meta(project_home, meta_type):
    """ Function for reading metadata from a project home.
    """
    if os.path.exists(f'{project_home}/{meta_type}_metadata.yml'):
        with open(
            f'{project_home}/{meta_type}_metadata.yml',
            'r',
            encoding='UTF-8',
        ) as stream:
            return yaml.safe_load(stream)
    return {}


def check_pids(project_home, running_via_slurm=False):
    """ Function to check if process IDs are still running.
    """
    pids = get_pids(project_home, running_via_slurm)
    if pids is None:
        return 'clear'
    if running_via_slurm:
        if check_slurm_job(str(pids[0])):
            return 'waiting'
    else:
        if psutil.pid_exists(int(pids[0])):
            return 'waiting'

    return 'done'

def check_slurm_job(job_id):
    """ Function to check is a slurm job is still running.
    """
    result = subprocess.run(
        ['squeue', '--job', job_id],
        stdout=subprocess.PIPE,
    )
    job_status = result.stdout.decode('utf-8')

    if job_id in job_status:
        return True
    return False

def subset_tasks(settings, tasks=None, mode=None):
    """ Function to subset all possible tasks to fetch
        the ones relevant for a given job.
    """
    if tasks is None:
        if mode == 'invitro':
            return INVITRO_TASKS
        elif mode == 'pisces':
            tasks = deepcopy(PISCES_TASK_NAMES)
        else:
            tasks = deepcopy(TASKS_NAMES)

        if settings.get('useCase') != 'proteomeAssembly':
            tasks = [task for task in tasks if task != 'translateGenome']
        if not settings.get('runCasa', False):
            tasks = [task for task in tasks if task != 'runCasa']
        if not settings.get('fragger', False):
            tasks = [task for task in tasks if task != 'fragger']
        if not settings.get('binding', False):
            tasks = [task for task in tasks if task != 'predictBinding']
        if not settings.get('pathogen', False):
            tasks = [task for task in tasks if task != 'extractCandidates']
        if not settings.get('quantify', False):
            tasks = [task for task in tasks if task != 'quantify']
    return tasks

def write_task_status(settings, project_home, tasks=None):
    """ Function to write the task status DataFrame. 
    """
    tasks = subset_tasks(settings, tasks, settings.get('variant'))
    if settings.get('variant') == 'invitro':
        task_names = [INVITRO_TASK_DESCRIPTIONS[task] for task in tasks]
    elif settings.get('variant') == 'pisces':
        task_names = [PISCES_TASK_DESCRIPTIONS[task] for task in tasks]
    else:
        task_names = [TASK_DESCRIPTIONS[task] for task in tasks]

    task_df = pd.DataFrame({
        'taskId': tasks,
        'taskName': task_names
    })
    task_df['taskIndex'] = task_df.index + 1
    task_df['status'] = 'Queued'
    task_df.to_csv(f'{project_home}/taskStatus.csv', index=False)

def format_header_and_footer(server_address):
    """ Helper function to add the server address to the interact-ms header and footer.
    """
    return {
        'INTERACT_HEADER': INTERACT_HEADER.format(
            server_address=server_address,
        ),
        'INTERACT_FOOTER': INTERACT_FOOTER.format(
            server_address=server_address,
        ),
    }
