import json
from dataclasses import asdict

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
# from dramatiq.middleware.prometheus import Prometheus
from dramatiq.results.backends import RedisBackend
from dramatiq.results import Results
import uuid
import os
from typing import List

from dacite import from_dict

from judger_error import JudgerError
from config import JUDGER_WORKSPACE, TEST_CASE_DIR
from compile_config import CompileConfig
from operation import Operation
from problem_info import ProblemInfo
from result import result
from run_config import RunConfig
from judger_task import Task

result_backend = RedisBackend(url="redis://container.ll-ap.cn:6379")
rabbitmq_broker = RabbitmqBroker(url="amqp://admin:admin@container.ll-ap.cn:5672")
rabbitmq_broker.add_middleware(Results(backend=result_backend))
# prometheus_middleware = Prometheus(http_host='0.0.0.0', http_port=9191)
# rabbitmq_broker.add_middleware(prometheus_middleware)

dramatiq.set_broker(rabbitmq_broker)


@dramatiq.actor(queue_name='judge', store_results=True)
def judge(task_id: str = None,
          problem_id: str = None,
          files: dict = None,
          operations: List[str] = None,
          config: dict = None):
    if task_id is None or problem_id is None:
        return
    
    print('Judging task %s' % task_id)

    # Assign main task id
    runner_id = str(uuid.uuid4())
    runner_path = os.path.join(JUDGER_WORKSPACE, runner_id)
    # Load judge task
    problem_info = ProblemInfo.load(problem_id)

    opts = []
    for op in operations:
        if config.__contains__(op):
            conf = config[op].copy()
            if not conf.__contains__('root_dir'):
                conf['root_dir'] = runner_path
        else:
            raise JudgerError('Cannot find config for operation [' + op + ']')
        if op == 'compile':
            opts.append(Operation(
                name=op,
                config=from_dict(
                    data_class=CompileConfig,
                    data=conf
                )))
        elif op == 'run':
            conf['problem_info'] = problem_info
            opts.append(Operation(
                name=op,
                config=from_dict(
                    data_class=RunConfig,
                    data=conf
                )))
        else:
            raise JudgerError('Unexpected operation')

    task = Task(task_id=task_id,
                problem_id=problem_id,
                runner_id=runner_id,
                runner_path=runner_path,
                files=files,
                operations=opts,
                problem_info=problem_info)

    try:
        task.write_files()
        res = task.run()
        # task.clean_up()
        # print(json.dumps(asdict(task), indent=2))
    except OSError as err:
        raise JudgerError(str(err))

    # result(res)
    # print(json.dumps(asdict(res), indent=2))
    return asdict(res)


if __name__ == '__main__':
    task_info = {
        'task_id': 'test_task',
        'problem_id': 'test',
        'files': {
            'main.cpp': '#include<iostream>\n'
                        '#include<cstdlib>\n'
                        'using namespace std;\n'
                        'int main() {\n'
                        '    int a, b;\n'
            # '    cerr << "ERROR" << endl;\n'
            # '    abort();\n'
                        '    cin >> a >> b;\n'
                        '    cout << a * b << " " << endl;\n'
                        '}\n',
        },
        'operations': ['compile', 'run'],
        'config': {
            'compile': {
                'command': '/usr/bin/g++ -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}',
                'src_name': 'main.cpp',
                'exe_name': 'main.o',
                'max_cpu_time': 1000,
                'max_real_time': 3000,
                'max_memory': 536870912
            },
            'run': {
                'command': '{exe_path}',
                'src_name': 'main.cpp',
                'exe_name': 'main.o',
                'max_cpu_time': 1000,
                'max_real_time': 3000,
                'max_memory': 536870912
            }
        }
    }
    message = judge.send(task_info['task_id'],
                         task_info['problem_id'],
                         task_info['files'],
                         task_info['operations'],
                         task_info['config'])
    print(message.get_result(block=True))
