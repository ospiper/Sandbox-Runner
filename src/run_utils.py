import hashlib


def handle_output(output) -> str:
    return '\n'.join([line.rstrip() for line in output.replace('\r\n', '\n').replace('\r','\n').rstrip().split('\n')])


def compare_output(raw: str = None, expected_md5: str = None) -> bool:
    return expected_md5 is not None and md5(raw) == expected_md5


def md5(s: str = None) -> str:
    return None if s is None else hashlib.md5(s.encode()).hexdigest()
