# Storj Node Reporter

This script calculates success rates for audits, downloads, uploads and repair traffic on Linux systems.
It then emails the statistics daily (including the previous day's statistics).

Alexey built a similar [script for windows](https://github.com/AlexeyALeonov/success_rate) users.

ReneSmeekes made a bash version that only prints to the console tool [here](https://github.com/ReneSmeekes/storj_success_rate). Much of the bash code comes from that project.

### How to use it

The program is a singular .py file.
The only requirements are the correct Python version (currently only supports 2.X) and installing required packages using pip.

Required pip packages:
- gmail
- schedule

`pip install gmail schedule`

It is recommended that you use [screen](https://ss64.com/bash/screen.html) if you are running this using an SSH connection.

### Example usage

Running using Python 2: `python node_reporter.py`

Running using Python 2 as root: `sudo python node_reporter.py`

Running using Python 2 in a screen: `screen python node_reporter.py`

Running using Python 2 in a screen as root: `screen sudo python node_reporter.py`

**Python 3 is not currently supported**

Running using Python 3: `python3 node_reporter.py`

Running using Python 3 as root: `sudo python3 node_reporter.py`

Running using Python 3 in a screen: `screen python3 node_reporter.py`

Running using Python 3 in a screen as root: `screen sudo python3 node_reporter.py`

Push the screen to the background by hitting **ctrl+a+d** simultaneously.

Return to the screen by typing `screen -R`

### Example output:
```
Sat 24 Aug 17:23:34 PDT 2019
========== AUDIT =============
Successful:           27035 (26943)
Recoverable failed:   398 (390)
Unrecoverable failed: 0 (0)
Success Rate Min:     98.549%
Success Rate Max:     100.000% (100.000%)
========== DOWNLOAD ==========
Successful:           757353 (742544)
Failed:               5079 (2059)
Success Rate:         99.334% (99.265%)
========== UPLOAD ============
Successful:           1366111 (1257413)
Rejected:             1936 (1455)
Failed:               154270 (134270)
Acceptance Rate:      99.858% (99.945%)
Success Rate:         89.853% (89.764%)
========== REPAIR DOWNLOAD ===
Successful:           4200 (4173)
Failed:               1337 (1332)
Success Rate:         79.674% (79.565%)
========== REPAIR UPLOAD =====
Successful:           24366 (21346)
Failed:               5884 (5453)
Success Rate:         80.549% (79.265%)
```

### CURRENT ISSUES AND TODO
- [ ] Update for Python 3
- [ ] Support other email services
- [ ] Include usage statistics (bandwidth, disk usage)
- [ ] Format information nicely (html, css, better readibality)
