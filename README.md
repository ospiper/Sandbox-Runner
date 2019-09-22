# Sandbox Runner

## Requirements
- Linux 2.6.23+
- libseccomp-dev
- libseccomp bindings for Python3 (Refer to [libseccomp](https://github.com/seccomp/libseccomp/blob/master/src/python/))

## Usage
```bash
python3 sandbox_runner.py [args] -- commands
# For Example
python3 sandbox_runner.py \
    -d \
    --max-cpu-time 1s \
    --max-real-time 3000ms \
    --max-memory 1g \
    --max-stack 512m \
    -c \
    -i /path/to/input \
    -o /path/to/output \
    -e /path/to/error \
    -l /path/to/log \
    -e VERSION=3 \
    -- \
    /usr/bin/python3 /path/to/script
```
|Arg (--arg)|Abbr (-a)|Required|Type|Desc|
|---|-----|--------|----|----|
|version|V|N|none|Display version info|
|help|h|N|none|Display help|
|debug|d|N|none|Enable debug log|
|||||
|max-cpu-time| |N|Number|Max CPU time (ms)|
|max-real-time| |N|Number|Max real time (ms)|
|max-memory| |N|Number|Max memory usage (Bytes)|
|memory-check-only|c|N|none|Check memory usage after it ends instead of killing it|
|max-stack| |N|Number|Max stack size (Bytes)|
|max-output-size| |N|Number|Max output size (Bytes)|
|max-process| |N|Number|Max # of processes|
|||||
|input-file|i|N|String|Absolute path of input file|
|output-file|o|N|String|Absolute path of output file|
|err-file|e|N|String|Absolute path of error file|
|log-file|l|N|String|Absolute path of log file|
|file-io|f|N|none|Enable file I/O for programs to run|
|||||
|env|v|N|String|Environment variables (Can be an array)|
|||||
|uid|u|N|Number|Runner uid|
|gid|g|N|Number|Runner gid|
|seccomp-rule|s|N|String|Seccomp rule to apply (Can be None)|