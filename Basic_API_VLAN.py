"""
This file contains multiple snippets of using API calls to manage VLANs in Infoblox.

You will need to find and replace the following to match your Infoblox deployment:
    1. <your_user_account> = Replace with the username you use to make API calls
    2. <your.infoblox.fqdn> = Replace with your Infoblox FQDN or IP address.

Note that anywhere you see a "_ref" value, that is just there as an example.  None
of the "_ref" values below represent a real Infoblox object.  You will need to use
one of the below API calls to obtain the real "_ref" values from your Infoblox environment.
    Example: "vlanrange/ZG5zLnZsYbF92bGFucy4zLjM5OQ:parent_view_name/vlan_range_name/1/100"
    Example: "vlan/ZG5zAuNjAuNTE:default/test_range_1/v100-TEST_VLAN1/100"
"""

import requests
from getpass import getpass
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(category=InsecureRequestWarning)

api_user = "<your_user_account>"
password = getpass("Enter your Infoblox password: ")
nios_base_url = "https://<your.infoblox.fqdn>/wapi/v2.10"

######################################################################################
# Below pulls down the "_ref" values for the different VLAN Views you have in Infoblox
######################################################################################

vl_view_ref_url = "https://<your.infoblox.fqdn>/wapi/v2.10/vlanview?"
vl_view_response = requests.get(vl_view_ref_url, auth=(api_user, password), verify=False, )
vl_view_JSON = vl_view_response.json()

print(vl_view_JSON)

######################################################################################
# Below pulls down the "_ref" values for the different VLAN Ranges you have in Infoblox
######################################################################################

vl_range_ref_url = "https://<your.infoblox.fqdn>/wapi/v2.10/vlanrange?"
vl_range_response = requests.get(vl_range_ref_url, verify=False, auth=(api_user, password))
vl_range_JSON = vl_range_response.json()

print(vl_range_JSON)

######################################################################################
# Below pulls down the "_ref" values for the a specific VLAN you have in Infoblox
######################################################################################

vlan_id = "100"
vl_ref_url = "https://<your.infoblox.fqdn>/wapi/v2.10/vlan?id={vlan_id}".format(vlan_id=vlan_id)
vl_response = requests.get(vl_ref_url, verify=False, auth=(api_user, password))
vl_JSON = vl_response.json()

print(vl_JSON)

######################################################################################
# Below pulls down all the VLANs within a parent VLAN.  Parent just means where the
# VLAN resides, whether it being in a VLAN view or range.
# You can get the VLAN parent "_ref" using the above API calls
######################################################################################

vl_range_parent_ref = "vlanrange/ZG5zLnZsYbF92bGFucy4zLjM5OQ:parent_view_name/vlan_range_name/1/100"

vl_parent_func = "/vlan?parent="
vl_parent_url = nios_base_url + vl_parent_func + vl_range_parent_ref
vl_parent_response = requests.get(vl_parent_url, verify=False, auth=(api_user, password))

for vlan in vl_parent_response.json():
    print(vlan)

######################################################################################
# Automatically create a new VLAN in the parent.  This grabs the next available VLAN
# Use the above API calls to get the parent VLAN ref
######################################################################################

vl_url = "https://<your.infoblox.fqdn>/wapi/v2.10/vlan"
vl_parent_ref = "vlanview/ZG5zLnZsYW5fdmlldyRkZWZhdWx0LjEuNDA5NA:default/1/4094"
vl_new_vl_name = "Test API Create"

vl_new_vlan_data = '{{"parent":{parent_ref}, ' \
                   '"id":"func:nextavailablevlanid:{parent_ref}", ' \
                   '"name":{vl_name}}}'.format(parent_ref=vl_parent_ref, vl_name=vl_new_vl_name)

vl_new_vlan_response = requests.post(vl_url, data=vl_new_vlan_data, verify=False, auth=(api_user, password))

print(vl_new_vlan_response.json())  # This prints the "_ref" value of the created VLAN

######################################################################################
# Below adds an existing VLAN to an existing network.
# You will need to use one of the above methods to get the "_ref" value for the
#   VLAN you want to add to the the existing network.
# You will also need to get the "_ref" value for the Network you are assigning
#   the VLAN too (not covered in this script).
######################################################################################


vl_ref_v100 = "vlan/ZG5zAuNjAuNTE:default/test_range_1/v100-TEST_VLAN1/100"  # Get this from above API calls
vl_ref_v200 = "vlan/ZG5zAuNjAuNTM:default/test_range_1/v200-TEST_VLAN2/200"  # Get this from above API calls

# Add single VLAN to a network
put_single_vlan_data = '{"vlans": [{"vlan": "' + vl_ref_v100 + '"}]}'
net_ref_net1 = "/network/ZG5zLm5ldHdvcmskMTAuMC4wLjAvMjcvMA:10.0.0.0/27/default"
put_single_vl_to_net_api = requests.put(nios_base_url + net_ref_net1, data=put_single_vlan_data, verify=False,
                                        auth=(api_user, password))

# Add multiple VLANs to a network
put_multi_vlan_data = '{"vlans": [{"vlan": "' + vl_ref_v100 + '"}, {"vlan": "' + vl_ref_v200 + '"}]}'
net_ref_net2 = "/network/ZG5zLm5ldHdvcmskMTAuMC4waoasdfaADF:10.10.0.0/24/default"
put_multi_vl_to_net_api = requests.put(nios_base_url + net_ref_net2, data=put_multi_vlan_data, verify=False,
                                       auth=(api_user, password))
