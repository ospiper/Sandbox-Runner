import json
import os
import sys
import uuid
import shutil
import zipfile
import re
from dataclasses import dataclass, asdict, field

import requests
from dacite import from_dict
from typing import List, Dict

from judger_worker import judge
from run_utils import md5
from config import BASE_URL


@dataclass
class ClientTask:
    name: str
    config: dict = field(default_factory=dict)


@dataclass
class FileTree:
    files: List[str] = field(default_factory=list)
    folders: Dict[str, 'FileTree'] = None


@dataclass
class ClientConfig:
    tasks: List[ClientTask] = field(default_factory=list)
    files: FileTree = None


def parse_file_tree(root: dict = None) -> FileTree:
    if root is None:
        return None
    files = root['files']
    folders = None
    if root['folders'] is not None:
        folders = dict()
        for k, v in root['folders'].items():
            folders[k] = parse_file_tree(v)
    return FileTree(files=files, folders=folders)


def parse_config(path: str):
    with open(path, 'r') as fin:
        config_data = json.loads(fin.read())
    tasks = [from_dict(data_class=ClientTask, data=task) for task in config_data['tasks']]
    files = parse_file_tree(config_data['files'])
    ret = ClientConfig(tasks=tasks, files=files)
    # print(json.dumps(asdict(ret), indent=2))
    return ret


def load_file_tree(tree: FileTree, root: str = None) -> dict:
    if tree is None:
        return None
    ret = dict()
    for file in tree.files:
        path = os.path.join(root, file)
        if os.path.exists(path):
            with open(path, 'r') as fin:
                ret[file] = fin.read()
        else:
            print('ENOENT', path)
    if tree.folders is not None:
        for f, t in tree.folders.items():
            ret[f] = load_file_tree(t, os.path.join(root, f))
    return ret


def load_user_files(tree: FileTree, root_path: str) -> dict:
    path = os.path.join(root_path, 'src')
    users = os.listdir(path)
    ret = dict()
    for user in users:
        ret[user] = load_file_tree(tree, os.path.join(path, user))
    return ret


def load_test_cases(root: str):
    case_root = os.path.join(root, 'std')
    temp_root = os.path.join(root, 'tmp')
    if os.path.exists(temp_root):
        shutil.rmtree(temp_root)
    os.makedirs(temp_root)
    sub_task_folders = [os.path.join(case_root, case) for case in os.listdir(case_root)]
    tasks = {'type': 'io'}
    sub_tasks = list()
    sub_task_id = 1
    for folder in sub_task_folders:
        if not os.path.isdir(folder):
            continue
        files = [os.path.join(folder, case) for case in os.listdir(folder)]
        filter(lambda f_str: f_str.endswith('.in'), files)
        cases = []
        s = {
            'sub_task_id': sub_task_id,
            'type': 'mul',
            'score': 0,
            'cases': None
        }
        case_id = 1
        in_files = list()
        for f in files:
            if not os.path.isfile(f):
                continue
            name = int(str(f.split(os.sep)[-1]).split('.')[0])
            ext = f.split('.')[-1]
            if ext == 'in':
                in_files.append(name)
        in_files.sort()
        # print(in_files)
        for f in in_files:
            input_path = os.path.join(folder, '%d.in' % f)
            output_path = os.path.join(folder, '%d.out' % f)
            if not os.path.isfile(output_path):
                in_files.remove(f)
                continue
            in_name = '%d_%d.in' % (sub_task_id, case_id)
            out_name = '%d_%d.out' % (sub_task_id, case_id)
            temp_in = os.path.join(temp_root, in_name)
            temp_out = os.path.join(temp_root, out_name)
            shutil.copyfile(input_path, temp_in)
            with open(output_path, 'r') as fin:
                output_str = '\n'.join([
                    l.rstrip() for l in fin.read().
                        replace('\r\n', '\n').
                        replace('\r', '\n').
                        split('\n')])
                with open(temp_out, 'w') as fout:
                    fout.write(output_str)
                    output_md5 = md5(output_str)
            cases.append({
                'case_id': case_id,
                'input_size': os.path.getsize(temp_in),
                'input_name': in_name,
                'output_size': os.path.getsize(temp_out),
                'output_name': out_name,
                'output_md5': output_md5
            })
            case_id += 1
        if len(cases) > 0:
            s['cases'] = cases
            sub_tasks.append(s)
            sub_task_id += 1
    score_per_sub_task = int(100 / len(sub_tasks))
    for t in sub_tasks:
        t['score'] = score_per_sub_task
    tasks['sub_tasks'] = sub_tasks
    with open(os.path.join(temp_root, 'tasks.json'), 'w') as task_out:
        task_out.write(json.dumps(tasks, indent=2))
    return tasks


def build_task_config(config: ClientConfig, root: str):
    problem_id = str(uuid.uuid4())
    operations = list()
    op_config = dict()
    load_test_cases(root)
    os.rename(os.path.join(root, 'tmp'), os.path.join(root, problem_id))
    for task in config.tasks:
        operations.append(task.name)
        op_config[task.name] = task.config
    return problem_id, operations, op_config


def zip_dir(dir_path, output_file_path):
    zip_file = zipfile.ZipFile(output_file_path, "w", zipfile.ZIP_DEFLATED)
    for path, dir_names, filenames in os.walk(dir_path):
        file_path = path.replace(dir_path, '')
        for filename in filenames:
            zip_file.write(os.path.join(path, filename), os.path.join(file_path, filename))
    zip_file.close()
    return output_file_path


def run_users(config: ClientConfig, users: dict, root: str):
    problem_id, operations, config = build_task_config(config, root)
    # print(task_id, problem_id, operations)
    # print(json.dumps(config, indent=2))
    messages = dict()
    user_list = list()
    zip_file = zip_dir(os.path.join(root, problem_id), os.path.join(root, '%s.zip' % problem_id))
    print('Transferring test cases...')
    files = {'file': open(zip_file, 'rb')}
    transfer_case = requests.post(BASE_URL + '/', files=files)
    if os.path.exists(os.path.join(root, problem_id)):
        shutil.rmtree(os.path.join(root, problem_id))
    if os.path.exists(zip_file):
        if not files['file'].closed:
            files['file'].close()
        os.remove(zip_file)
    if transfer_case.content.decode() != problem_id:
        problem_id = transfer_case.content.decode()
    for user, files in users.items():
        task_id = str(uuid.uuid4())
        user_list.append(user)
        messages[user] = judge.send(task_id=task_id,
                                    problem_id=problem_id,
                                    files=files,
                                    operations=operations,
                                    config=config)
        print('Judging', user)
    results = dict()
    for user in user_list:
        print('Retrieving results of ' + user + '...')
        result = messages[user].get_result(block=True, timeout=60*1000)
        results[user] = result
    print('Cleaning up...')
    requests.post(BASE_URL + '/clean_up', data={'problem_id': problem_id})
    # print(json.dumps(results, indent=2))
    return results


if __name__ == '__main__':
    print(os.getcwd())
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        os.chdir(sys.argv[1])
    print(os.getcwd())
    config = parse_config('config.json')
    users = load_user_files(config.files, os.getcwd())
    # print(json.dumps(users, indent=2))
    # print(json.dumps([asdict(task) for task in config.tasks], indent=2))
    results = run_users(config, users, os.getcwd())
    report_path = os.path.join(os.getcwd(), 'report')
    if os.path.exists(report_path):
        shutil.rmtree(report_path)
    os.makedirs(report_path)
    for user, result in results.items():
        user_id = user
        if result['results'].__contains__('compile'):
            compile_res = result['results']['compile']
            compile_result = 'success' if compile_res['success'] else 'fail'
            compile_error = compile_res['info']['stderr']
        else:
            compile_error = ''
            compile_result = 'Ignored'
        if result['results'].__contains__('run'):
            run_res = result['results']['run']
            run_result = 'success' if run_res['success'] else 'fail'
            score = run_res['info']['score']
            output_run = True
        else:
            output_run = False
            run_result = 'ignored'
            score = 0

        with open(os.path.join(os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1]), 'template.html'), 'r') as t_in:
            template = t_in.read()
        template = template.replace('{{compile_result}}', compile_result) \
            .replace('{{compile_error}}', compile_error) \
            .replace('{{user_id}}', user_id) \
            .replace('{{run_result}}', run_result) \
            .replace('{{score}}', str(score))
        reg = r'^\s*{{foreach case \|(.+)}}\s*$'
        case_match = re.search(reg, template, re.M | re.I)
        if case_match:
            rep = case_match.group(0)
            # print(rep)
            run_template = ''
            if output_run:
                fields = [s.strip() for s in case_match.group(1).split('|')]
                cases = []
                for sub_task in run_res['info']['sub_tasks']:
                    for c in sub_task['cases']:
                        c['sub_task_id'] = sub_task['sub_task_id']
                        c['type'] = sub_task['type']
                        c['score'] = sub_task['score']
                        cases.append(c)
                for c in cases:
                    line = '<tr>'
                    for f in fields:
                        line += '<td>' + str(c[str(f)]) + '</td>'
                    line += '</tr>'
                    run_template += line
            template = template.replace(rep, run_template)
        with open(os.path.join(report_path, '%s.html' % user), 'w') as t_out:
            t_out.write(template)
            print('User {} exported.'.format(user))
