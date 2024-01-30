#Auto Schedule Workshop SDDCs
# Amaury Garde
# Updated: 01/2023
# imports
import arrow as arw


# functions
def define_crontab(event):
    # deployment times in EST for CT
    sddc_deploy = "16:00:00"  # sunday
    hcx_deploy = "10:00:00"  # monday
    vcdr_deploy = "10:00:00"  # wednesday
    sddc_delete = "22:00:00"  # thursday

    deploy_sddc = arw.get(event['start']['date'] + ' ' + sddc_deploy).shift(days=-1)
    deploy_hcx = arw.get(event['start']['date'] + ' ' + hcx_deploy)
    deploy_vcdr = arw.get(event['start']['date'] + ' ' + vcdr_deploy).shift(days=2)
    delete_sddc = arw.get(event['start']['date'] + ' ' + sddc_delete).shift(days=3)

    # password change
    pwd_change = deploy_hcx.format('MMMMYYYY').lower()
    pwd_change = pwd_change[:3] + pwd_change[-4:]

    if 'amer' in event['summary'].lower():
        hd_sddc = deploy_sddc
        hd_hcx = deploy_hcx
        hd_vcdr = deploy_vcdr
        hdl_sddc = delete_sddc

    elif 'emea' in event['summary'].lower():
        deploy_sddc = deploy_sddc.replace(tzinfo='CET')
        deploy_hcx = deploy_hcx.replace(tzinfo='CET')
        deploy_vcdr = deploy_vcdr.replace(tzinfo='CET')
        delete_sddc = delete_sddc.replace(tzinfo='CET')

        hd_sddc = deploy_sddc.to('US/Eastern')
        hd_hcx = deploy_hcx.to('US/Eastern')
        hd_vcdr = deploy_vcdr.to('US/Eastern')
        hdl_sddc = delete_sddc #.to('US/Eastern')

    elif 'apj' in event['summary'].lower():
        deploy_sddc = deploy_sddc.replace(tzinfo='Australia/Sydney')
        deploy_hcx = deploy_hcx.replace(tzinfo='Australia/Sydney')
        deploy_vcdr = deploy_vcdr.replace(tzinfo='Australia/Sydney')
        delete_sddc = delete_sddc.replace(tzinfo='Australia/Sydney')

        hd_sddc = deploy_sddc.to('US/Eastern')
        hd_hcx = deploy_hcx.to('US/Eastern')
        hd_vcdr = deploy_vcdr.to('US/Eastern')
        hdl_sddc = delete_sddc #.to('US/Eastern')

    return pwd_change, hd_sddc.format('mm HH DD MM') + ' *', hd_hcx.format('mm HH DD MM') + ' *', hd_vcdr.format(
        'mm HH DD MM') + ' *', hdl_sddc.format('mm HH DD MM') + ' *', deploy_sddc.format(
        'YYYY-MM-DD HH:mm'), deploy_hcx.format('YYYY-MM-DD HH:mm'), deploy_vcdr.format(
        'YYYY-MM-DD HH:mm'), delete_sddc.format('YYYY-MM-DD HH:mm'), hd_sddc.format('YYYY-MM-DD HH:mm'), hd_hcx.format(
        'YYYY-MM-DD HH:mm'), hd_vcdr.format('YYYY-MM-DD HH:mm'), hdl_sddc.format('YYYY-MM-DD HH:mm')
