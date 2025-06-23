""" Script for running inSPIRE as a string to be formatted.
"""

INSPIRE_INVITRO_SCRIPT = """
import os
import sys
import traceback
import subprocess

from interact_ms.queue_manager import (
    add_to_queue,
    check_queue,
    remove_from_queue,
    update_status,
)

def execute_taks(home_key, project_home, task_list, proc_id):
    ''' Function which runs in the background, running inSPIRE tasks and
    interacting with interact-ms queue.
    '''
    task_list = task_list.split(',')
    config_file = '{project_home}/config.yml'
    add_to_queue(project_home, home_key)
    check_queue(project_home, home_key)
    update_status(
        project_home,
        home_key,
        'start',
        '0',
    )

    for task in task_list:
        try:
            if task == 'runMSFragger':
                sub_proc = subprocess.run([
                    'python', f'{project_home}/outputFolder/inspire_invitro/run_ms_fragger.py', '--config_file', f'{project_home}/config_fragger.yml',
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                sub_proc = subprocess.run([
                    'apptainer', 'run', f'--bind', f'{project_home}:/mnt',
                    f'{apptainer_image}', task, '{spliced_upper_limit}'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('hey', sub_proc.stdout)
            print('ok', sub_proc.stdout.decode('utf-8'))
            try:
                print('ok', sub_proc.stderr.decode('utf-8'))
            except:
                print('stderr is empty')
            status = sub_proc.returncode
            print(status, type(status))
        except Exception as e:
            print('interact-ms failed on task ' + task  + 'with Exception:' + str(e))
            print(traceback.format_exc())
            status = '1'

        status = str(status)
        update_status(
            project_home,
            home_key,
            task,
            status,
        )
        if status != '0':
            if task not in ('predictBinding', 'quantify', 'generateReport'):
                remove_from_queue(home_key, proc_id)
                sys.exit(0)
    remove_from_queue(home_key, proc_id)

if __name__ == '__main__':
    proc_id = os.getpid()
    with open(f'{project_home}/job_pids.txt', 'w', encoding='UTF-8') as pid_file:
        pid_file.writelines(str(proc_id)+'\\n')
    execute_taks('{home_key}', '{project_home}', '{task_list}', proc_id)
    sys.exit(0)

"""
