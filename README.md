# Sandbox Runner

## Requirements
- libseccomp-dev
- python3-seccomp (in Ubuntu 19.04+)

## Usage
```bash
python3 safe_run.py [args] -- commands
```
|Arg|Short|Required|Type|Desc|
|---|-----|--------|----|----|
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