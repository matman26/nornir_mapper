from nornir.core.task import Task, Result
from ttp import ttp

cdp_entry_template = """
<doc>
-------------------------
Device ID: R2.lab.local
Entry address(es):
  IP address: 2.2.2.2
Platform: Cisco 3725,  Capabilities: Router Switch IGMP
Interface: FastEthernet0/1,  Port ID (outgoing port): FastEthernet0/0
Holdtime : 126 sec

Version :
Cisco IOS Software, 3700 Software (C3725-ADVENTERPRISEK9-M), Version 12.4(15)T7, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2008 by Cisco Systems, Inc.
Compiled Wed 13-Aug-08 21:36 by prod_rel_team

advertisement version: 2
VTP Management Domain: ''
Duplex: half
</doc>

<group name="{{neighbor_name}}">
Device ID: {{ neighbor_name }}
  IP address: {{ neighbor_address }}
Platform: {{ platform_string | ORPHRASE }},  Capabilities: {{ device_capabilities | ORPHRASE }}
Interface: {{ local_interface | ORPHRASE}},  Port ID (outgoing port): {{ remote_interface | ORPHRASE }}
</group>
"""

def map_neighbors(task: Task, *args, **kwargs) -> Result:
    """Uses CDP to grab neighbor data and return result as dictionary."""
    net_connect = task.host.get_connection('netmiko', task.nornir.config)
    result_data = net_connect.send_command('show cdp neighbors detail', **kwargs)
    parser = ttp(data=result_data,template=cdp_entry_template)
    parser.parse()
    results = parser.result(format='raw')[0][0]

    return Result(
        result=results,
        changed=False,
        host=task.host)
