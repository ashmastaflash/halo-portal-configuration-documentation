#! /usr/local/bin/python

# Author: Sean Nicholson
# Script for exporting Halo API information for documenting a Halo portal
# Version: 1.1
# Date: 04/20/2017
# ############################################################################


import json, io
import cloudpassage

from collections import OrderedDict
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


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
            group_details = byteify(group_details)
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
                if len(group_details['fim_policies']) > 0:
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
                        lids_policies_details = lids_policies_details + "(Inherited) " + lids_policies['name'].strip() + "; "


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




            row="{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(str(group_details['name']).encode("ascii", "ignore").strip(), str(group_details['tag']).encode("ascii", "ignore").strip(),str(group_parent_name).encode("ascii", "ignore").strip(), str(group_details['has_children']).encode('utf-8').strip(), fw_policies_details, csm_policies_details, fim_policies_details, lids_policies_details, alert_profile_details, se_policies_details)
            outfile.write(row)
        print "Processing of Groups Data Complete"
        outfile.close()


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



def policies_csv(session):
    get_policies = cloudpassage.HttpHelper(session)
    list_of_csm_policies = get_policies.get_paginated("/v1/policies", "policies", 10)
    list_of_lids_policies = get_policies.get_paginated("/v1/lids_policies", "lids_policies", 10)
    list_of_fim_policies = get_policies.get_paginated("/v1/fim_policies", "fim_policies", 10)
    list_of_fw_policies = get_policies.get_paginated("/v1/firewall_policies", "firewall_policies", 10)
    total_policies = len(list_of_csm_policies) + len(list_of_lids_policies) + len(list_of_fim_policies) + len(list_of_fw_policies)
    policy_counter = 1
    with open('policies.csv', 'w') as outfile3:
        outfile3.write("Policy Type,Policy Name,Platform,Group Owner,Shared,Used By, Created by,Created,Updated by,Updated\n")
        print "Processing Policies"
        for policy in list_of_csm_policies:
            print "Processing Policy {0} of {1}".format(policy_counter, total_policies)
            policy_counter += 1
            used_by_group =""
            if "used_by" in policy:
                policy_applied_groups = policy['used_by']
                for policy_group in policy_applied_groups:
                    used_by_group += policy_group['name'] + ";"
            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(policy['module'], policy['name'].replace(",",""), policy['platform'], policy['group_name'], policy['shared'], used_by_group, policy['created_by'], policy['created_at'], policy['updated_by'], policy['updated_at']  )
            outfile3.write(row)
        for policy in list_of_lids_policies:
            print "Processing Policy {0} of {1}".format(policy_counter, total_policies)
            policy_counter += 1
            used_by_group =""
            if "used_by" in policy:
                policy_applied_groups = policy['used_by']
                for policy_group in policy_applied_groups:
                    used_by_group += policy_group['name'] + ";"
            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(policy['module'], policy['name'].replace(",","").encode('utf-8').strip(), policy['platform'], policy['group_name'].encode('utf-8').strip(), policy['shared'], used_by_group.encode('utf-8').strip(), policy['created_by'], policy['created_at'].encode('utf-8').strip(), policy['updated_by'], policy['updated_at'].encode('utf-8').strip()  )
            outfile3.write(row)
        for policy in list_of_fim_policies:
            print "Processing Policy {0} of {1}".format(policy_counter, total_policies)
            policy_counter += 1
            used_by_group =""
            if "used_by" in policy:
                policy_applied_groups = policy['used_by']
                for policy_group in policy_applied_groups:
                    used_by_group += policy_group['name'] + ";"
            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(policy['module'], policy['name'].replace(",",""), policy['platform'], policy['group_name'], policy['shared'], used_by_group, policy['created_by'], policy['created_at'], policy['updated_by'], policy['updated_at']  )
            outfile3.write(row)
        for policy in list_of_fw_policies:
            print "Processing Policy {0} of {1}".format(policy_counter, total_policies)
            policy_counter += 1
            used_by_group =""
            if "used_by" in policy:
                policy_applied_groups = policy['used_by']
                for policy_group in policy_applied_groups:
                    used_by_group += policy_group['name'] + ";"
            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(policy['module'], policy['name'].replace(",",""), policy['platform'], policy['group_name'], policy['shared'], used_by_group, policy['created_by'], policy['created_at'], policy['updated_by'], policy['updated_at']  )
            outfile3.write(row)
    print "Policy processing complete"
    outfile3.close()

def alert_profiles_csv(session):
    get_policies = cloudpassage.HttpHelper(session)
    list_of_alert_profiles = get_policies.get_paginated("/v1/alert_profiles", "alert_profiles", 10)
    with open('alert_profiles.csv', 'w') as outfile4:
        outfile4.write("Policy Name,Alert Frequency,Group Owner,Shared,Used By,Created by,Created,Updated by,Updated\n")
        print "Processing Alert Profiles"
        for policy in list_of_alert_profiles:
            used_by_group =""
            if "used_by" in policy:
                policy_applied_groups = policy['used_by']
                for policy_group in policy_applied_groups:
                    used_by_group += policy_group['name'] + ";"
            row = "{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(policy['name'].replace(",",""), policy['frequency'], policy['group_name'], policy['shared'], used_by_group, policy['created_by'], policy['created_at'], policy['updated_by'], policy['updated_at']  )
            outfile4.write(row)
        print "Alert Profiles processing complete"
        outfile4.close()

def main():
    api_session = None
    api_session = create_api_session(api_session)
    get_users(api_session)
    list_groups(api_session)
    policies_csv(api_session)
    alert_profiles_csv(api_session)


if __name__ == "__main__":
    main()
