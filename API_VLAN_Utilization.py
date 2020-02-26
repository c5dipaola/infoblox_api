"""
This script is used to show you the VLAN utilization of the VLANs specified.

You will need to find and replace the following to match your Infoblox deployment:
    1. <your_user_account> = Replace with the username you use to make API calls
    2. <your.infoblox.fqdn> = Replace with your Infoblox FQDN or IP address.

Note that anywhere you see a "_ref" value, that is just there as an example.  None
of the "_ref" values below represent a real Infoblox object.  You will need to obtain the real "_ref" values
from your Infoblox environment.
    Example: "vlanrange/ZG5zLnZsYbF92bGFucy4zLjM5OQ:parent_view_name/vlan_range_name/1/100"
    Example: "vlan/ZG5zAuNjAuNTE:default/test_range_1/v100-TEST_VLAN1/100"


"""

from getpass import getpass
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(category=InsecureRequestWarning)


def auth_request(url_root, username, password_input):
    """
    This function makes an initial API call to Infoblox DDI returns the session cookie to memory
    for future use in the execution of API calls in this script.  Each time the script is run, a new session cookie
    is taken, then flushed from memory upon script completion.

    To use, assign a variable to this function and include the below required input:

    :param url_root: Infoblox base URL.
        - Infoblox base URL example = https://infoblox.domain.com/wapi/v2.10
    :param string username: The username used to authenticate to the API
    :param password_input: The password for authenticating to Infoblox.
    :return: Returns session cookie to use for further API calls.

    Example:
        nios_base_url = https://infoblox.domain.com/wapi/v2.10 <-- variable for "url_root"
        username = "api_username"
        password = getpass("Enter the password: ") <-- Securely get "password_input"
        cookiejar = auth_request(nios_base_url, username, password) <-- Assign this function to variable
        api_call = requests.get(url, cookies=cookiejar, verify=False) <-- use "cookiejar" for API calls
    """
    url = url_root + "/smartfolder:personal?_return_as_object=1"
    try:
        response = requests.get(url, auth=(username, password_input), verify=False)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # Whoops it wasn't a 200
            print("ERROR: Infoblox DDI reported an error {} while authenticating.".format(response.status_code))
            return False
    except requests.exceptions.RequestException:
        # A serious problem happened, like an SSLError or InvalidURL
        print("WARN: Unable to authenticate with Infoblox DDI.")
        return False
    print("INFO: Successfully authenticated to Infoblox DDI.")
    return response.cookies


def get_ddi_vlans(base_url, parent_ref, cookies):
    """

    :param base_url: Infoblox URL including the "/vlan?parent=" function
    :param parent_ref: Infoblox "parent" VLAN info.  This is also called the VLAN "_ref" value
    :param cookies: This is the variable name you assigned for the authentication cookie
    :return: Returns a nested dictionary of all the VLANs in a given view or range
        Example returned dictionary value of vlans in a view:
            {'v3': {'id': 3, 'name': 'v3-10.1.3.0m24'}, 'v4': {'id': 4, 'name': 'EXCLUDE'}}
        Example of how to iterate through each of the VLANs to extract the ID or name:

            nios_cookiejar = auth_request(nios_base_url, password)
            response = get_ddi_vlans(base_url_parent_ddi, dc_l3_parent_ref, nios_cookiejar)
            for key, value in response.items():
                print(value['id'], value['name'])
    """
    vlans = {}
    vl_parent_func = "/vlan?parent="
    url = base_url + vl_parent_func + parent_ref
    response = requests.get(url, cookies=cookies, verify=False)
    for item in response.json():
        vlans[f"v{item['id']}"] = {"id": item['id'], "name": item['name']}
    return vlans


api_user = "<your_user_account>"
password = getpass("Enter your Infoblox password: ")

######################

######################

nios_base_url = "https://<your.infoblox.fqdn>/wapi/v2.10"
dc_l3_parent_ref = "vlanrange/ZG5zLnZsYW5y4zLjM5OQ:my_network_view/dc_l3_vlans/1/499"
dc_l2_parent_ref = "vlanrange/ZG5zLnZscy41MDAuNTk5:my_network_view/dc_l2_only_vlans/500/999"
cookiejar = auth_request(nios_base_url, api_user, password)

########################################################################
# Datacenter L3 VLAN information below
########################################################################

dc_l3_exclude = []
dc_l3_used_vlans = []

dc_l3_response = get_ddi_vlans(nios_base_url, dc_l3_parent_ref, cookiejar)
for key, value in dc_l3_response.items():
    if value['name'] not in "EXCLUDE":
        dc_l3_used_vlans.append(value['id'])
    else:
        dc_l3_exclude.append(value['id'])

dc_l3_vlan_range = list(range(0, 498))  # 0-498 because Python index starts at 0, not 1
dc_l3_total_consumed_vlans = len(dc_l3_exclude) + len(dc_l3_used_vlans)
dc_l3_vlans_available = len(dc_l3_vlan_range) - dc_l3_total_consumed_vlans

print("\n" + "*" * 60 + "\nDatacenter Layer 3 VLAN Utilization Details\n" + "*" * 60)
print(f"Datacenter Layer 3 VLAN Range size = {len(dc_l3_vlan_range)}")
print(f"Datacenter Layer 3 VLANs in use = {len(dc_l3_used_vlans)}")
print(f"Datacenter Layer 3 VLANs excluded from use = {len(dc_l3_exclude)}")
print(f"Datacenter Layer 3 VLANs consumed total = {dc_l3_total_consumed_vlans}")
print(f"Datacenter Layer 3 VLANs available for use = {dc_l3_vlans_available}")

# ########################################################################
# # Datacenter L2 Only VLAN information below
# ########################################################################


dc_l2_exclude = []
dc_l2_used_vlans = []

dc_l2_response = get_ddi_vlans(nios_base_url, dc_l2_parent_ref, cookiejar)
for key, value in dc_l2_response.items():
    if value['name'] not in "EXCLUDE":
        dc_l2_used_vlans.append(value['id'])
    else:
        dc_l2_exclude.append(value['id'])

dc_l2_vlan_range = list(range(499, 998))  # 499-998 because Python index starts at 0, not 1
dc_l2_total_consumed_vlans = len(dc_l2_exclude) + len(dc_l2_used_vlans)
dc_l2_vlans_available = len(dc_l2_vlan_range) - dc_l2_total_consumed_vlans

print("\n" + "*" * 60 + "\nDatacenter Layer 2 VLAN Utilization Details\n" + "*" * 60)
print(f"Datacenter Layer 2 VLAN Range size = {len(dc_l2_vlan_range)}")
print(f"Datacenter Layer 2 VLANs in use = {len(dc_l2_used_vlans)}")
print(f"Datacenter Layer 2 VLANs excluded from use = {len(dc_l2_exclude)}")
print(f"Datacenter Layer 2 VLANs consumed total = {dc_l2_total_consumed_vlans}")
print(f"Datacenter Layer 2 VLANs available for use = {dc_l2_vlans_available}")
