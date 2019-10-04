from config import TEST_CASE_DIR, JUDGER_WORKSPACE
from judger_error import JudgerError
from runner_config import RunnerConfig
from compiler_config import CompilerConfig
from judge_task import JudgeCase, JudgeSubTask, JudgeTask
from judge_result import *
import sandbox
import os
import json
import shutil


def load_judge_task(problem_id=None):
    if problem_id is None or not isinstance(problem_id, str):
        return
    task_path = os.path.join(TEST_CASE_DIR, problem_id, 'tasks.json')
    try:
        fp = open(task_path, 'r')
        data = json.load(fp)
        fp.close()
        ret = JudgeTask(data['task_type'])
        for sub_task in data['sub_tasks']:
            cases = []
            for case in sub_task['cases']:
                cases.append(JudgeCase(case_id=case['case_id'],
                                       input_size=case['input_size'],
                                       input_name=case['input_name'],
                                       output_size=case['output_size'],
                                       output_name=case['output_name'],
                                       output_md5=case['output_md5']))
            ret.sub_tasks.append(JudgeSubTask(sub_task['sub_task_id'], sub_task['sub_task_type'], sub_task['score'], cases))
        return ret
    except IOError:
        raise JudgerError('Cannot find tasks of problem %s' % problem_id)
    except ValueError as valErr:
        raise JudgerError(str(valErr))


def create_file_tree(path=None, files=None):
    if not isinstance(files, dict):
        raise JudgerError('Files must be a dict()')
    for p, f in files.items():
        if not isinstance(p, str):
            raise JudgerError('Unexpected path name: ' + str(p))
        if '/' in p or '\\' in p:
            raise JudgerError('Path can only be single-depth relative path')
        if p.startswith('..'):
            raise JudgerError('Path cannot be parent path')
        if isinstance(f, str):
            try:
                with open(os.path.join(path, p), 'w') as fp:
                    fp.write(f)
            except IOError:
                raise JudgerError('Cannot write ' + p)
        elif isinstance(f, dict):
            try:
                real_path = os.path.join(path, p)
                os.makedirs(real_path)
                create_file_tree(real_path, f)
            except OSError:
                raise JudgerError('Cannot create path ' + p)
        else:
            raise JudgerError('Unexpected file entry: ' + str(p))


def write_files(root=None, files=None):
    if root is None or files is None:
        return
    if not isinstance(root, str) or not isinstance(files, dict):
        return
    try:
        os.makedirs(root)
    except OSError:
        raise JudgerError('Main task directory already exists')
    create_file_tree(root, files)


def clean_up(root=None):
    if root is None or not isinstance(root, str):
        return
    if not root.startswith(JUDGER_WORKSPACE):
        return
    if os.path.exists(root):
        try:
            for root, dirs, files in os.walk(root, False):
                print(root)
                shutil.rmtree(root)
        except OSError:
            raise JudgerError('Cannot remove path ' + root)


def run_compile(compiler_config=None):
    print(compiler_config)
    if not isinstance(compiler_config, CompilerConfig):
        raise JudgerError('Cannot find compiler config')
    path = compiler_config.root_dir
    max_output_size = '1g'
    if not isinstance(compiler_config.command, str):
        raise JudgerError('Command must be a string')
    src_path = os.path.join(path, compiler_config.src_name)
    src_dir = path
    exe_path = os.path.join(path, compiler_config.exe_name)
    exe_dir = path
    command = compiler_config.command.format(src_path=src_path,
                                             src_name=compiler_config.src_name,
                                             src_dir=src_dir,
                                             exe_path=exe_path,
                                             exe_name=compiler_config.exe_name,
                                             exe_dir=exe_dir).split(' ')
    sandbox.run(command,
                max_cpu_time=compiler_config.max_cpu_time,
                max_real_time=compiler_config.max_real_time,
                max_memory=compiler_config.max_memory,
                max_output_size=max_output_size,
                memory_check_only=compiler_config.memory_check_only,
                max_stack=compiler_config.max_stack,
                max_process=compiler_config.max_process,
                env={'PATH': os.getenv('PATH')})


def run_judge_case(case=None, runner_config=None):
    if case is None or not isinstance(case, JudgeCase):
        raise JudgerError('Cannot find test case')
    if not isinstance(runner_config, RunnerConfig):
        raise JudgerError('Cannot find runner config')
    path = runner_config.root_dir
    max_output_size = '256m'
    exe_path = os.path.join(path, runner_config.exe_name)
    exe_dir = path
    if runner_config.command is not None and isinstance(runner_config.command, str):
        runner_config.command = runner_config.command.format(exe_path=exe_path,
                                                             exe_name=runner_config.exe_name,
                                                             exe_dir=exe_dir).split(' ')
    # TODO: Run case in sandbox
    return JudgeCaseResult(case_id=case.case_id,
                          cpu_time=None,
                          real_time=None,
                          memory=None,
                          signal=None,
                          exit_code=None,
                          result=None,
                          error=None)


def run_judge_sub_task(sub_task=None, runner_config=None):
    if sub_task is None or not isinstance(sub_task, JudgeSubTask):
        raise JudgerError('Cannot find sub task')
    if not isinstance(runner_config, RunnerConfig):
        raise JudgerError('Cannot find runner config')
    ret = JudgeSubTaskResult()
    ret.sub_task_id = sub_task.sub_task_id
    ret.sub_task_type = sub_task.sub_task_type
    ac_count = 0
    for case in sub_task.cases:
        case_result = run_judge_case(case, runner_config)
        ret.add_case(case_result)
        if case_result.result == RESULT_ACCEPTED:
            ac_count += 1
    # Organize cases results
    if ret.sub_task_type == 'add':
        ret.score = int(sub_task.score * (ac_count / len(sub_task.cases)))
    elif ret.sub_task_type == 'mul':
        if ac_count == len(ret.cases):
            ret.score = sub_task.score
    else:
        raise JudgerError('Unrecognized sub task type')
    return ret


def run_judge_task(task=None, runner_config=None):
    if task is None or not isinstance(task, JudgeTask):
        raise JudgerError('Cannot find judge task')
    if not isinstance(runner_config, RunnerConfig):
        raise JudgerError('Cannot find runner config')
    result = JudgeTaskResult()
    result.task_type = task.task_type

    for sub_task in task.sub_tasks:
        try:
            sub_task_result = run_judge_sub_task(sub_task, runner_config)
            result.add_sub_task(sub_task_result)
            result.score += sub_task_result.score
            for case_result in sub_task_result.cases:
                result.cpu_time += case_result.cpu_time
                result.real_time += case_result.real_time
                result.peak_memory = max(result.peak_memory, case_result.memory)
                if case_result.result in (RESULT_RUNTIME_ERROR, RESULT_SYSTEM_ERROR):
                    result.result = case_result.result
                elif case_result.result == RESULT_WRONG_ANSWER:
                    result.result = RESULT_WRONG_ANSWER
                elif case_result.result != RESULT_ACCEPTED:
                    result.result = case_result.result
                if case_result.error is not None:
                    result.error = case_result.error
        except JudgerError as err:
            result.message = str(err)
    return result


if __name__ == '__main__':
    
    tasks = load_judge_task('1')
    print(json.dumps(tasks.to_dict(), indent=2))
    exit(0)
    compiler_config = CompilerConfig.build({
        'command': '/usr/bin/gcc -lm -DONLINE_JUDGE -o {exe_path} {src_path}',
        'src_name': 'main.c',
        'exe_name': 'main',
        'max_cpu_time': '5s',
        'max_real_time': '15s',
        'max_memory': '1g'
    })
    compiler_config.root_dir = os.path.join(JUDGER_WORKSPACE, '1')
    run_compile(compiler_config)
    clean_up(os.path.join(JUDGER_WORKSPACE, '1'))
    write_files(
        os.path.join(JUDGER_WORKSPACE, '1'),
        {
            'main.py': 'print(\'hello world\')',
            'src': {
                '__init__.py': '# init',
                'blah': {
                    'hey.json': '[1, 2, 3, 4]'
                }
            }
        }
    )
    runner_config = RunnerConfig.build({
        'command': '/usr/bin/gcc -lm -DONLINE_JUDGE -o {exe_path} {src_path}',
        'src_name': 'main.c',
        'exe_name': 'main',
        'max_cpu_time': '5s',
        'max_real_time': '15s',
        'max_memory': '1g'
    })
    exit(0)
    runner_config.root_dir = os.path.join(JUDGER_WORKSPACE, '1')
    run_judge_task(tasks, runner_config)
