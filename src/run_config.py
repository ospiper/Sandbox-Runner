from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from execute_config import ExecuteConfig
from problem_info import ProblemInfo


@dataclass
class RunConfig(ExecuteConfig):
    problem_info: ProblemInfo = None
