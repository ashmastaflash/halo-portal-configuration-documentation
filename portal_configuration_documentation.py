#! /usr/local/bin/python

# Author: Sean Nicholson
# Script for exporting Halo API information for documenting a customer's portal

import json, io
import cloudpassage

from collections import OrderedDict
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


def create_api_session(session):
    config_file_loc = "cloudpassage.yml"
    config_info = cloudpassage.ApiKeyManager(config_file=config_file_loc)
    session = cloudpassage.HaloSession(config_info.key_id, config_info.secret_key)

    return session

def list_groups(session):
    groups = cloudpassage.HttpHelper(session)
    list_of_groups = groups.get_paginated("/v2/groups", "groups", 10)
    group_number_total = len(list_of_groups)
    group_counter = 1

    with open('groups.csv', 'wb') as outfile:
        outfile.write("Group Name, Tag, Parent Group, Has Children, FW Policies, CSM Policies, FIM Policies, LIDS Policies, AP Policies, SE Policies\n")
        for group in list_of_groups:
            group_parent_name = ""
            fw_policies_details = ""
            csm_policies_details = ""
            fim_policies_details = ""
            lids_policies_details = ""
            alert_profile_details = ""
            se_policies_details = ""
            print "Processing {0} of {1} Groups - Group Name {2}".format(group_counter, group_number_total, group['name'])
            group_counter += 1
            group_details_raw = groups.get("/v2/groups/" + group['id'])
            group_details = group_details_raw['group']
            #print group_details
            if group_details['parent_id']:
                group_parent_details = groups.get("/v2/groups/" + group_details['parent_id'])
                group_parent_name = group_parent_details['group']['name']
            else:
                group_parent_name = "None"
            if group_details['firewall_policies']:
                if len(group_details['firewall_policies']) > 1:
                    for fw_policies in group_details['firewall_policies']:
                        fw_policies_details = fw_policies_details + fw_policies['name'].encode('utf-8').strip() + "; "
                else:
                    for fw_policies in group_details['firewall_policies']:
                        fw_policies_details = fw_policies['name'].encode('utf-8').strip()

            if group_details['csm_policies']:
                if len(group_details['csm_policies']) > 1:
                    for csm_policies in group_details['csm_policies']:
                        csm_policies_details = csm_policies_details + csm_policies['name'].encode('utf-8').strip() + "; "
                else:
                    for csm_policies in group_details['csm_policies']:
                        csm_policies_details = csm_policies['name'].encode('utf-8').strip()
            if 'inherited_csm_policies' in group_details:
                if group_details['inherited_csm_policies']:
                    if csm_policies_details and "; " not in csm_policies_details:
                        csm_policies_details = csm_policies_details + "; "
                    for csm_policies in group_details['inherited_csm_policies']:
                        csm_policies_details = csm_policies_details + "(Inherited) " + csm_policies['name'].encode('utf-8').strip() + "; "


            if group_details['fim_policies']:
                if len(group_details['fim_policies']) > 1:
                    for fim_policies in group_details['fim_policies']:
                        fim_policies_details = fim_policies_details + fim_policies['name'] + "; "
                else:
                    fim_policies_details = group_details['fim_policies']['name']
            if 'inherited_fim_policies' in group_details:
                if group_details['inherited_fim_policies']:
                    if fim_policies_details and "; " not in fim_policies_details:
                        fim_policies_details = fim_policies_details + "; "
                    for fim_policies in group_details['inherited_fim_policies']:
                        fim_policies_details = fim_policies_details + "(Inherited) " +fim_policies['name'].encode('utf-8').strip() + "; "


            if group_details['lids_policies']:
                if len(group_details['lids_policies']) > 1:
                    for lids_policies in group_details['lids_policies']:
                        lids_policies_details = lids_policies_details + lids_policies['name'] + "; "
                else:
                    for lids_policies in group_details['lids_policies']:
                        lids_policies_details = lids_policies['name'].encode('utf-8').strip()
            if 'inherited_lids_policies' in group_details:
                if group_details['inherited_lids_policies']:
                    if lids_policies_details and "; " not in lids_policies_details:
                        lids_policies_details = lids_policies_details + "; "
                    for lids_policies in group_details['inherited_lids_policies']:
                        lids_policies_details = lids_policies_details + "(Inherited) " + lids_policies['name'].encode('utf-8').strip() + "; "


            if group_details['alert_profiles']:
                if len(group_details['alert_profiles']) > 1:
                    for alert_profile in group_details['alert_profiles']:
                        alert_profile_details = alert_profile_details + alert_profile['name'] + "; "
                else:
                    for alert_profile in group_details['alert_profiles']:
                        alert_profile_details = alert_profile['name'].encode('utf-8').strip()

            if group_details['special_events_policy']:
                #if len(group_details['special_events_policy']) > 1:
                #    for se_policies in group_details['special_events_policy']:
                #        se_policies_details = se_policies['name'] + "; "
                #else:
                se_policies_details = group_details['special_events_policy']['name'].encode('utf-8').strip()




            row="{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(str(group_details['name']).encode('utf-8').strip(), str(group_details['tag']).encode('utf-8').strip(),str(group_parent_name).encode('utf-8').strip(), str(group_details['has_children']).encode('utf-8').strip(), fw_policies_details, csm_policies_details, fim_policies_details, lids_policies_details, alert_profile_details, se_policies_details)
            outfile.write(row)
        outfile.close()
        #group_format = json.dumps(list_of_groups, indent=4,sort_keys=False, separators=(',',':'))
        #outfile.write(to_unicode(group_format))

def list_groups2 (session):
    list_of_group_details = {}
    groups2 = cloudpassage.HttpHelper(session)
    groups2_list = json.loads(groups2.get("/v2/groups"))
    for eachGroup in groups2_list:
        #print
        groupID = eachGroup['id']
        print groupID
        group2_details = groups2.get("/v2/groups/" + groupID)
        list_of_group_details = list_of_group_details + group2_details
    with open('groups2.txt', 'w') as outfile:
        group2_format = json.dumps(list_of_group_details, indent=4,sort_keys=False, separators=(',',':'))
        outfile.write(to_unicode(group2_format))

def get_users(session):
    users = cloudpassage.HttpHelper(session)
    list_of_users = users.get_paginated("/v2/users", "users", 10)
    with open('users.csv', 'w') as outfile:
        outfile.write("Last Name, First Name, Username, Email, Active, Access Group Level, Access Role, Last Login, Created\n")
        user_format = json.dumps(list_of_users, indent=4,sort_keys=False, separators=(',',':'))
        length_of_user_list = len(list_of_users)
        user_count = 1
        for user in list_of_users:
            user_access = user['access']
            print "Processing {0} of {1} users".format(user_count, length_of_user_list)
            #print user_access
            group_level_access_detail = users.get('/v1/groups/' + user_access[0]['group_id'])
            group_access_name = group_level_access_detail['group']['name']
            group_access_role = str(user_access[0]['roles'][0])

            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(user['lastname'],user['firstname'],user['username'],user['email'],user['active'], group_access_name, group_access_role, user['last_login_at'], user['created_at'])
            outfile.write(row)
            user_count += 1
        #outfile.write(to_unicode(user_format))
        print "Processing of User data complete"
        outfile.close()




def main():
    api_session = None
    api_session = create_api_session(api_session)
    get_users(api_session)
    list_groups(api_session)

    #list_groups2(api_session)


if __name__ == "__main__":
    main()
