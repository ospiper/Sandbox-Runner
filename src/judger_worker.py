import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware.prometheus import Prometheus
import uuid
import json
import os
import shutil

from judger_error import JudgerError, CompileError
from config import JUDGER_WORKSPACE
from judger import load_judge_task, write_files, run_compile, run_judge_task, clean_up
from judger_result import result
from compiler_config import CompilerConfig
from runner_config import RunnerConfig
from judge_task import JudgeCase, JudgeSubTask, JudgeTask

rabbitmq_broker = RabbitmqBroker(url="amqp://admin:admin@container.ll-ap.cn:5672")
prometheus_middleware = Prometheus(http_host='0.0.0.0', http_port=9191)
rabbitmq_broker.add_middleware(prometheus_middleware)

dramatiq.set_broker(rabbitmq_broker)


@dramatiq.actor(queue_name='judge')
def judge(task_id,
          problem_id,
          user_id,
          lint=False,
          leak=False,
          files=None,
          compiler_config=None,
          runner_config=None):
    if task_id is None or problem_id is None or user_id is None:
        return
    if not isinstance(task_id, str) or not isinstance(problem_id, str) or not isinstance(user_id, str):
        return
    if compiler_config is None or runner_config is None:
        return
    if not isinstance(compiler_config, dict) or not isinstance(runner_config, dict):
        return

    # Assign main task id
    main_task_id = uuid.uuid4()
    main_task_path = os.path.join(JUDGER_WORKSPACE, str(main_task_id))

    # Parse configurations
    try:
        compiler_config = CompilerConfig.build(compiler_config)
        compiler_config.root_dir = main_task_path
    except ValueError:
        raise JudgerError('Cannot parse compiler config')

    try:
        runner_config = RunnerConfig.build(runner_config)
        runner_config.root_dir = main_task_path
    except ValueError:
        raise JudgerError('Cannot parse runner config')

    # Load judge task
    task = None
    try:
        task = load_judge_task(problem_id)
    except JudgerError as err:
        result(False, None, str(err))

    # Write files
    try:
        write_files(main_task_path, files)
    except JudgerError as err:
        result(False, None, str(err))

    # Run compiler
    try:
        run_compile(compiler_config)
    except CompileError as err:
        result(False, None, str(err))

    # Run judge task
    judge_results = None
    try:
        judge_results = run_judge_task(task, runner_config)
    except JudgerError as err:
        result(False, None, str(err))

    # Organize return VO
    if judge_results is not None:
        judge_results.task_id = task_id
        judge_results.problem_id = problem_id
        judge_results.user_id = user_id

    # Clean up
    try:
        clean_up(main_task_path)
    except JudgerError as err:
        result(False, None, str(err))

    # Return
    if judge_results is not None:
        result(True, judge_results.to_dict())
    else:
        result(False, None)
