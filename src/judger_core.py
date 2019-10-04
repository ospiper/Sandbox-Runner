from runner_config import RunnerConfig
import sandbox


def handle_output(output):
    return '\n'.join([line.rstrip() for line in output.replace('\r\n', '\n').replace('\r','\n').rstrip().split('\n')])


def judge(runner_config=None,
          case_id=None,
          input_name=None,
          output_md5=None):
    run_result = sandbox.run(command=(),
                             max_cpu_time=None,
                             max_real_time=None,
                             max_memory=None,
                             memory_check_only=None,
                             max_stack=None,
                             max_output_size=None,
                             max_process=None,
                             input_file=None,
                             output_file=None,
                             err_file=None,
                             log_file=None,
                             file_io=None,
                             env=None,
                             uid=None,
                             gid=None,
                             seccomp_rule=None)
