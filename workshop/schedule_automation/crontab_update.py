# Auto Schedule Workshop SDDCs
# Amaury Garde
# Updated: 04/2023


# imports
import os.path
import datetime
# from crontab import CronTab

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from timzone_conversion import *

# scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# templates
templates_list = [
    "vmcexpert1-01,vmcexpert1-02,vmcexpert1-03,vmcexpert1-04,vmcexpert1-05,vmcexpert1-06,vmcexpert1-07,vmcexpert1-08,vmcexpert1-09,vmcexpert1-10,vmcexpert1-11,vmcexpert1-12,vmcexpert1-13,vmcexpert1-14,vmcexpert1-15,vmcexpert1-instructor",
    "vmcexpert1-01,vmcexpert1-02,vmcexpert1-03,vmcexpert1-04,vmcexpert1-05,vmcexpert1-06,vmcexpert1-07,vmcexpert1-08,vmcexpert1-instructor",
    "VMCEXPERT2-01,VMCEXPERT2-02,VMCEXPERT2-03,VMCEXPERT2-04,VMCEXPERT2-05,VMCEXPERT2-06,VMCEXPERT2-07,VMCEXPERT2-08,VMCEXPERT2-09,VMCEXPERT2-10,VMCEXPERT2-11,VMCEXPERT2-12,VMCEXPERT2-13,VMCEXPERT2-14,VMCexpert2-15,VMCEXPERT2-INSTRUCTOR",
    "VMCEXPERT2-01,VMCEXPERT2-02,VMCEXPERT2-03,VMCEXPERT2-04,VMCEXPERT2-05,VMCEXPERT2-06,VMCEXPERT2-07,VMCEXPERT2-08,VMCEXPERT2-INSTRUCTOR",
    "vmcexpert3-01,vmcexpert3-02,vmcexpert3-03,vmcexpert3-04,vmcexpert3-05,vmcexpert3-06,vmcexpert3-07,vmcexpert3-08,vmcexpert3-09,vmcexpert3-10,vmcexpert3-11,vmcexpert3-12,vmcexpert3-13,vmcexpert3-14,vmcexpert3-15,vmcexpert3-instructor",
    "vmcexpert3-01,vmcexpert3-02,vmcexpert3-03,vmcexpert3-04,vmcexpert3-05,vmcexpert3-06,vmcexpert3-07,vmcexpert3-08,vmcexpert3-instructor"
]
password_template = "VMC{}!"

crontab_base = """# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command \n\n"""

# authentication
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow()  # .isoformat() + 'Z'  # 'Z' indicates UTC time
    end = (now + datetime.timedelta(days=7)).isoformat() + 'Z'
    events_result = service.events().list(calendarId='uh1m5qmeeoq0lh9vl6njgm1v1c@group.calendar.google.com',
                                          timeMin=(now.isoformat() + 'Z'), timeMax=end,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    f = open('crontab_jobs.txt', 'w')
    f.truncate(0)
    f.write(crontab_base)

    email_body = ""

    # for testing only
    # events = events[2:]

    # separate VCE & MCM
    vce = list()
    mcm = list()
    emea = list()
    for event in events:
        if 'vmc' in event['summary'].lower():
            vce.append(event)
        elif 'mcm' in event['summary'].lower():
            mcm.append(event)

    # error if more than 3 workshops
    if (len(vce) + len(mcm)) > 3:
        # todo: include in email
        print("Too many workshops that week")
        exit()

    if (len(vce) + len(mcm)) == 3:
        for i in range(len(mcm)):
            if 'emea' in mcm[i]['summary'].lower() and len(emea) < 1:
                emea = [mcm[i]]
                mcm = [x for j, x in enumerate(mcm) if j != i]

        if len(mcm) < 2:
            for i in range(len(vce)):
                if 'emea' in vce[i]['summary'].lower() and len(emea) < 1:
                    emea = [vce[i]]
                    vce = [x for j, x in enumerate(vce) if j != i]

    all_ordered = vce + mcm + emea

    tracker = 0
    orgs_tracker = 1
    for event in all_ordered:
        start = event['start'].get('dateTime', event['start'].get('date'))

        # prepare time
        pwd_change, sddc_deploy, hcx_deploy, vcdr_deploy, sddc_delete, sddc_deploy_local, hcx_deploy_local, vcdr_deploy_local, sddc_delete_local, sddc_deploy_ec2, hcx_deploy_ec2, vcdr_deploy_ec2, sddc_delete_ec2 = define_crontab(
            event)

        # track if populated
        command_delete_vcdr = [None] * 0

        if len(vce) == 0:
            orgs_tracker += 1
            tracker += 2

        if 'vmc' in event['summary'].lower():
            if orgs_tracker == 3:
                command_deploy_sddc = "/git/hank/skyler/vmcworkshop/scripts/create-sddc.sh vmcexpert3 eu-central-1".format(
                    orgs_tracker)
                command_deploy_hcx = "/git/hank/skyler/vmcworkshop/scripts/deploy-hcx.sh vmcexpert3 eu-central-1"
                command_deploy_vcdr = "/git/hank/skyler/vmcworkshop/scripts/create-vcdr.sh vmcexpert3 us-west-2 vmcexpert3-vcdr01"
                command_delete_sddc = "/git/hank/skyler/vmcworkshop/scripts/delete-sddc.sh vmcexpert3 eu-central-1 all"
                command_delete_vcdr = "/git/hank/skyler/vmcworkshop/scripts/delete-sddc.sh vmcexpert3 us-west-2 vmcexpert3-vcdr01"
            else:
                command_deploy_sddc = "/git/hank/skyler/vmcworkshop/scripts/create-sddc.sh vmcexpert{0} us-west-2".format(
                    orgs_tracker)
                command_deploy_hcx = "/git/hank/skyler/vmcworkshop/scripts/deploy-hcx.sh vmcexpert{0} us-west-2".format(
                    orgs_tracker)
                command_deploy_vcdr = "/git/hank/skyler/vmcworkshop/scripts/create-vcdr.sh vmcexpert{0} us-west-2 vmcexpert{0}-vcdr01".format(
                    orgs_tracker)
                command_delete_sddc = "/git/hank/skyler/vmcworkshop/scripts/delete-sddc.sh vmcexpert{0} us-west-2 all".format(
                    orgs_tracker)

            if "30 person" in event['summary'].lower():
                command_deploy_sddc += " " + templates_list[tracker] + " " + password_template.format(
                    pwd_change) + " AWS"
                command_deploy_hcx += " " + templates_list[tracker][:209]
                command_deploy_vcdr += " " + password_template.format(pwd_change) + " AWS"

            elif "16 person" in event['summary'].lower():
                command_deploy_sddc += " " + templates_list[tracker + 1] + " " + password_template.format(
                    pwd_change) + " AWS"
                command_deploy_hcx += " " + templates_list[tracker + 1][:111]
                command_deploy_vcdr += " " + password_template.format(pwd_change) + " AWS"

            f.write("\n\n# These cronjobs are for : " + event['summary'])
            if orgs_tracker == 3:
                f.writelines(
                    ['\n' + sddc_deploy + ' ' + command_deploy_sddc, '\n' + hcx_deploy + ' ' + command_deploy_hcx,
                     '\n' + vcdr_deploy + ' ' + command_deploy_vcdr,
                     '\n' + sddc_delete + ' ' + command_delete_sddc,
                     '\n' + sddc_delete + ' ' + command_delete_vcdr])
            else:
                f.writelines(
                    ['\n' + sddc_deploy + ' ' + command_deploy_sddc, '\n' + hcx_deploy + ' ' + command_deploy_hcx,
                     '\n' + vcdr_deploy + ' ' + command_deploy_vcdr,
                     '\n' + sddc_delete + ' ' + command_delete_sddc])

            email_body += "<br><br>Schedule for " + event['summary'] + ' : <br><br>'
            email_body += "SDDC deployment : " + sddc_deploy_local + ' Local Time, ' + sddc_deploy_ec2 + ' EST time' + '<br>'
            email_body += "HCX deployment : " + hcx_deploy_local + ' Local Time, ' + hcx_deploy_ec2 + ' EST time' + '<br>'
            email_body += "VCDR deployment : " + vcdr_deploy_local + ' Local Time, ' + vcdr_deploy_ec2 + ' EST time' + '<br>'
            email_body += "SDDC deletion : " + sddc_delete_local + ' Local Time, ' + sddc_delete_ec2 + ' EST time' + '<br>'

        else:
            if orgs_tracker == 3 and len(vce) != 0:
                command_deploy_sddc = "/git/hank/skyler/cmvmcworkshop/scripts/create-sddc-cm3.sh vmcexpert3 eu-central-1"
                command_delete_sddc = "/git/hank/skyler/cmvmcworkshop/scripts/delete-sddc-cm.sh vmcexpert3 eu-central-1 all"

            else:
                command_deploy_sddc = "/git/hank/skyler/cmvmcworkshop/scripts/create-sddc-cm2.sh vmcexpert2 us-west-2"
                command_delete_sddc = "/git/hank/skyler/cmvmcworkshop/scripts/delete-sddc-cm.sh vmcexpert2 us-west-2 all"

            if "30 person" in event['summary'].lower():
                command_deploy_sddc += " " + templates_list[tracker] + " " + password_template.format(
                    pwd_change) + " AWS"
            elif "15 person" in event["summary"].lower():
                command_deploy_sddc += " " + templates_list[tracker + 1] + " " + password_template.format(
                    pwd_change) + " AWS"

            f.write("\n\n# These cronjobs are for : " + event['summary'])
            f.writelines(
                ['\n' + sddc_deploy + ' ' + command_deploy_sddc, '\n' + sddc_delete + ' ' + command_delete_sddc])

            email_body += "<br><br>Schedule for " + event['summary'] + ' : <br><br>'
            email_body += "SDDC deployment : " + sddc_deploy_local + ' Local Time, ' + sddc_deploy_ec2 + ' EST time' + '<br>'
            email_body += "SDDC deletion : " + sddc_delete_local + ' Local Time, ' + sddc_delete_ec2 + ' EST time' + '<br>'

        tracker += 2
        orgs_tracker += 1

    f.write("\n\n# Default daily status jobs")
    f.writelines(["\n00 23 * * * /git/hank/skyler/vmcworkshop/scripts/status-sddc.sh vmcexpert1 us-west-2 all",
                  "\n00 23 * * * /git/hank/skyler/vmcworkshop/scripts/status-sddc.sh vmcexpert2 us-west-2 all",
                  "\n00 23 * * * /git/hank/skyler/vmcworkshop/scripts/status-sddc.sh vmcexpert3 us-west-2 all",
                  "\n00 09 * * SAT docker run -i -w /tmp/scripts/skyler/schedule_automation -v /git/hank:/tmp/scripts schedule_automation:latest python3 crontab_update.py",
                  "\n05 09 * * SAT crontab /git/hank/skyler/schedule_automation/crontab_jobs.txt\n\n"])

    f.close()

except HttpError as error:
    print('An error occurred: %s' % error)
