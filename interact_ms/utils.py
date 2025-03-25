""" Utility functions for interact-ms.
"""
from copy import deepcopy
import os
import time

import pandas as pd
import psutil
import yaml

from interact_ms.constants import (
    INTERACT_HOME_KEY,
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

    params_config = read_meta(project_home, 'parameters')
    print(params_config)
    search_config = read_meta(project_home, 'search')


    tasks = deepcopy(TASKS_NAMES)
    print(variant, tasks)

    if not search_config['runFragger']:
        tasks = [task for task in tasks if task != 'fragger']
    if params_config['useBindingAffinity'] not in ['asValidation', 'asFeature']:
        tasks = [task for task in tasks if task != 'predictBinding']
    if variant != 'pathogen':
        tasks = [task for task in tasks if task != 'extractCandidates']
    if not params_config['runQuantification']:
        tasks = [task for task in tasks if task != 'quantify']
    print(variant, tasks)
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
    for task in tasks:
        html_table += f'''
            <tr align="center" valign="center" text-align="left">
            <td>{task}</td>
			<td>{TASK_DESCRIPTIONS[task]}</td>
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


def safe_job_id_fetch(project_home):
    """ Fetch the job ID of a job if it exists.
    """
    if not os.path.exists(f'{project_home}/job_pids.txt'):
        time.sleep(2)

    if os.path.exists(f'{project_home}/job_pids.txt'):
        with open(f'{project_home}/job_pids.txt', 'r', encoding='UTF-8') as pid_file:
            return int(pid_file.readline().strip())
    return 0

def get_pids(project_home):
    """ Function to get the pids
    """
    if not os.path.exists(f'{project_home}/job_pids.txt'):
        time.sleep(3)
        if not os.path.exists(f'{project_home}/job_pids.txt'):
            return None

    with open(f'{project_home}/job_pids.txt', 'r', encoding='UTF-8') as file:
        lines = file.readlines()
        pids = [line.rstrip() for line in lines]
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


def check_pids(project_home):
    """ Function to check if process IDs are still running.
    """
    pids = get_pids(project_home)
    if pids is None:
        return 'clear'
    if psutil.pid_exists(int(pids[0])):
        return 'waiting'

    return 'done'


def subset_tasks(settings, tasks=None):
    """ Function to subset all possible tasks to fetch
        the ones relevant for a given job.
    """
    if tasks is None:
        tasks = deepcopy(TASKS_NAMES)
        if not settings['fragger']:
            tasks = [task for task in tasks if task != 'fragger']
        if not settings['binding']:
            tasks = [task for task in tasks if task != 'predictBinding']
        if not settings['pathogen']:
            tasks = [task for task in tasks if task != 'extractCandidates']
        if not settings['quantify']:
            tasks = [task for task in tasks if task != 'quantify']
    return tasks

def write_task_status(settings, project_home, tasks=None):
    """ Function to write the task status DataFrame. 
    """
    tasks = subset_tasks(settings, tasks)
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
