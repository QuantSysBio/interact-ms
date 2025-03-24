""" Script for running inSPIRE as a string to be formatted.
"""

INSPIRE_SCRIPT = """
import os
import sys
import traceback

from inspire.run import run_inspire

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
    print(f'adding {task_list} to queue')
    add_to_queue(project_home, home_key)
    print(f'added {task_list} to queue')
    check_queue(project_home, home_key)
    print(f'check_queue {task_list} to queue')
    update_status(
        project_home,
        home_key,
        'start',
        '0',
    )

    for task in task_list:
        try:
            run_inspire(task, config_file)
            status = '0'
        except Exception as e:
            print('interact-ms failed on task' + task  + 'with Exception:' + str(e))
            print(traceback.format_exc())
            status = '1'

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
