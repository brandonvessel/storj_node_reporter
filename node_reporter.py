banner = '''\033[0;92m
888b    888               888              8888888b.                                     888                     
8888b   888               888              888   Y88b                                    888                     
88888b  888               888              888    888                                    888                     
888Y88b 888  .d88b.   .d88888  .d88b.      888   d88P  .d88b.  88888b.   .d88b.  888d888 888888  .d88b.  888d888 
888 Y88b888 d88""88b d88" 888 d8P  Y8b     8888888P"  d8P  Y8b 888 "88b d88""88b 888P"   888    d8P  Y8b 888P"   
888  Y88888 888  888 888  888 88888888     888 T88b   88888888 888  888 888  888 888     888    88888888 888     
888   Y8888 Y88..88P Y88b 888 Y8b.         888  T88b  Y8b.     888 d88P Y88..88P 888     Y88b.  Y8b.     888     
888    Y888  "Y88P"   "Y88888  "Y8888      888   T88b  "Y8888  88888P"   "Y88P"  888      "Y888  "Y8888  888     
                                                               888                                               
                                                               888                                               
                                                               888 

Title:    Node Reporter
Author:   Brandon Vessel
Github:   https://github.com/brandonvessel/storj_node_reporter
Version:  1.1
Purpose:  Periodically email system administrators concerning their Storj V3 Storagenode's daily statistics according to the log file.
'''

print(banner)

from gmail import GMail, Message
import os
import schedule
import subprocess
from time import sleep


#### CONFIG ####
EMAIL_TIME = "08:00" # default 08:00 which is 8am
SLEEP_TIME = 10
EMAIL_SENDTO = "*****@*****.***"
EMAIL_USERNAME = "*****@gmail.com"
EMAIL_PASSWORD = "*****"
EMAIL_SPACING = "standard"


#### NODE INFO ####
NODE_NICKNAME = "*****"
DOCKER_NODE_NAME="${1:-storagenode}"
LOG="docker logs {}".format(DOCKER_NODE_NAME)


## FIRST RUN CHECK ##
if(not os.path.isfile("node_report.txt")):
    lines = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # Open file for editing
    open_file = open("node_report.txt", "wb")

    # Write data
    for line in lines:
        open_file.write(str(line) + "\n")

    # Close file
    open_file.close()


def get_stats():
    lines = open("node_report.txt", 'rb').readlines()
    for i in range(0,len(lines)):
        lines[i] = lines[i].rstrip()
    return lines


def run_command(command):
    # We sleep so we don't work the machine too hard :)
    sleep(SLEEP_TIME)
    print("RUNNING: {}".format(command))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output


def generate_report():
    ### GET DATE ####
    the_date = run_command("date").rstrip()

    # audit
    audit_success = run_command("{} 2>&1 | grep GET_AUDIT | grep downloaded -c".format(LOG)).rstrip()
    audit_failed_warn = run_command("{} 2>&1 | grep GET_AUDIT | grep failed | grep -v open -c".format(LOG)).rstrip()
    audit_failed_crit = run_command("{} 2>&1 | grep GET_AUDIT | grep failed | grep open -c".format(LOG)).rstrip()
    if(str(audit_success) == "0" and str(audit_failed_warn) == "0" and str(audit_failed_crit) == "0"):
        audit_success_min = "0%"
        audit_success_max = "0%"
    else:
        audit_success_min = "{}%".format(float(audit_success) / (float(audit_failed_warn) + float(audit_success) + float(audit_failed_crit))*100.0)
        audit_success_max = "{}%".format(float(audit_success) / (float(audit_failed_crit) + float(audit_success))*100.0)

    # download
    down_success = run_command('''{} 2>&1 | grep '"GET"' | grep downloaded -c'''.format(LOG)).rstrip()
    down_failed = run_command('''{} 2>&1 | grep '"GET"' | grep failed -c'''.format(LOG)).rstrip()
    if(str(down_success) == '0' and str(down_failed) == '0'):
        down_rate = "0%"
    else:
        down_rate = "{}%".format(float(down_success) / (float(down_success) + float(down_failed))*100.0)

    # upload
    upload_success = run_command('''{} 2>&1 | grep '"PUT"' | grep uploaded -c'''.format(LOG)).rstrip()
    upload_rejected = run_command('''{} 2>&1 | grep rejected | grep upload -c'''.format(LOG)).rstrip()
    upload_failed = run_command('''{} 2>&1 | grep '"PUT"' | grep failed -c'''.format(LOG)).rstrip()
    if(str(upload_success) == "0" and str(upload_rejected) == "0" and str(upload_failed) == "0"):
        upload_accept_rate = "0%"
        upload_success_rate = "0%"
    else:
        upload_accept_rate = "{}%".format(float(upload_success) / (float(upload_success) + float(upload_rejected))*100.0)
    if(str(upload_success) != "0"):
        upload_success_rate = "{}%".format(float(upload_success) / (float(upload_success) + float(upload_failed))*100.0)
    else:
        upload_success_rate = "0%"

    # repair download
    repair_down_success = run_command('''{} 2>&1 | grep GET_REPAIR | grep downloaded -c'''.format(LOG)).rstrip()
    repair_down_failed = run_command('''{} 2>&1 | grep GET_REPAIR | grep failed -c'''.format(LOG)).rstrip()
    if(str(repair_down_failed) == "0" and str(repair_down_success) == "0"):
        repair_down_rate = "0%"
    else:
        repair_down_rate = "{}%".format(float(repair_down_success) / (float(repair_down_success) + float(repair_down_failed))*100.0)

    # repair upload
    repair_upload_success = run_command('''{} 2>&1 | grep PUT_REPAIR | grep uploaded -c'''.format(LOG)).rstrip()
    repair_upload_failed = run_command('''{} 2>&1 | grep PUT_REPAIR | grep failed -c'''.format(LOG)).rstrip()
    if(str(repair_upload_failed) == "0" and str(repair_upload_success) == "0"):
        repair_upload_rate = "0%"
    else:
        repair_upload_rate = "{}%".format(float(repair_upload_success) / (float(repair_upload_success) + float(repair_upload_failed))*100.0)


    ## GET STATS ##
    stat_list = get_stats()


    ## RECORD STATS ##
    lines = [audit_success, audit_failed_warn, audit_failed_crit, audit_success_min, audit_success_max, down_success, down_failed, down_rate, upload_success, upload_rejected, upload_failed, upload_accept_rate, upload_success_rate, repair_down_success, repair_down_failed, repair_down_rate, repair_upload_success, repair_upload_failed, repair_upload_rate]
    
    # Open file for editing
    open_file = open('node_report.txt', 'wb')

    # Write data
    for line in lines:
        open_file.write(str(line) + "\n")

    # Close file
    open_file.close()


    ## GENERATE REPORT ##
    if(EMAIL_SPACING == "standard"):
        report = '''{}
======== AUDIT ===========
Successful:           {} ({})
Recoverable failed:   {} ({})
Unrecoverable failed: {} ({})
Success Rate Min:     {} ({})
Success Rate Max:     {} ({})
======== DOWNLOAD ========
Successful:           {} ({})
Failed:               {} ({})
Success Rate:         {} ({})
======== UPLOAD ==========
Successful:           {} ({})
Rejected:             {} ({})
Failed:               {} ({})
Acceptance Rate:      {} ({})
Success Rate:         {} ({})
======== REPAIR DOWNLOAD =
Successful:           {} ({})
Failed:               {} ({})
Success Rate:         {} ({})
======== REPAIR UPLOAD ===
Successful:           {} ({})
Failed:               {} ({})
Success Rate:         {} ({})'''.format(the_date, audit_success, stat_list[0], audit_failed_warn, stat_list[1], audit_failed_crit, stat_list[2], audit_success_min, stat_list[3], audit_success_max, stat_list[4], down_success, stat_list[5], down_failed, stat_list[6], down_rate, stat_list[7], upload_success, stat_list[8], upload_rejected, stat_list[9], upload_failed, stat_list[10], upload_accept_rate, stat_list[11], upload_success_rate, stat_list[12], repair_down_success, stat_list[13], repair_down_failed, stat_list[14], repair_down_rate, stat_list[15], repair_upload_success, stat_list[16], repair_upload_failed, stat_list[17], repair_upload_rate, stat_list[18])    
    elif(EMAIL_SPACING == "single"):
        report = '''{}
======== AUDIT ===========
Successful: {}
Recoverable failed: {}
Unrecoverable failed: {}
Success Rate Min: {}
Success Rate Max: {}
======== DOWNLOAD ========
Successful: {}
Failed: {}
Success Rate: {}
======== UPLOAD ==========
Successful: {}
Rejected: {}
Failed: {}
Acceptance Rate: {}
Success Rate: {}
======== REPAIR DOWNLOAD =
Successful: {}
Failed: {}
Success Rate: {}
======== REPAIR UPLOAD ===
Successful: {}
Failed: {}
Success Rate: {}'''.format(the_date, audit_success, audit_failed_warn, audit_failed_crit, audit_success_min, audit_success_max, down_success, down_failed, down_rate, upload_success, upload_rejected, upload_failed, upload_accept_rate, upload_success_rate, repair_down_success, repair_down_failed, repair_down_rate, repair_upload_success, repair_upload_failed, repair_upload_rate)    

    return report


def send_email():

    report = generate_report()
    print(report)

    gmail = GMail('Storj Notification <{}>'.format(EMAIL_USERNAME), password=EMAIL_PASSWORD)
    message = Message("Daily Storj Report For Node {}".format(NODE_NICKNAME), to=EMAIL_SENDTO, text=report)

    gmail.send(message)


if __name__ == '__main__':
    # Schedule daily email
    schedule.every().day.at(EMAIL_TIME).do(send_email)
    
    # Send test email
    gmail = GMail('Storj Notification <{}>'.format(EMAIL_USERNAME), password=EMAIL_PASSWORD)
    message = Message("Daily Storj Report For Node {}".format(NODE_NICKNAME), to=EMAIL_SENDTO, text='If you are receiving this, you have configured your email correctly! :)')
    gmail.send(message)

    while True:
        schedule.run_pending()
        sleep(60)