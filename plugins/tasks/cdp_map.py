from nornir.core.task import Task, Result
from ttp import ttp

cdp_template = """
<vars>
INTF = "[A-Z][a-zA-Z]+\s[/0-9]+"
</vars>
<group name="{{device_name}}">
{{ device_name }} {{ local_interface | re("INTF")}} {{ holdtime}} {{ capability_string }} {{ platform | re("WORD") }} {{ port_id | re("INTF")}}
</group>
"""

cdp_entry_template = """
<group name="{{neighbor_name}}">
Device ID: {{ neighbor_name }}
  IP address: {{ neighbor_address }}
Platform: {{ platform_string | ORPHRASE }},  Capabilities: {{ device_capabilities | ORPHRASE }}
</group>
"""

def map_neighbors(task: Task, *args, **kwargs) -> Result:
    """Uses CDP to grab neighbor data and return result as dictionary."""
    net_connect = task.host.get_connection('netmiko', task.nornir.config)
    result_data = net_connect.send_command('show cdp neighbors', **kwargs)
    parser = ttp(data=result_data,template=cdp_template)
    parser.parse()
    results = parser.result(format='raw')[0][0]

    cdp_data = {}
    #print(results)
    for neighbor in results:
        #print(f"show cdp entry {neighbor}")
        neighbor_data = net_connect.send_command(f"show cdp entry {neighbor}")
        entry_parser = ttp(data=neighbor_data, template=cdp_entry_template)
        entry_parser.parse()
        cdp_data.update(**entry_parser.result(format='raw')[0][0])

    return Result(
        result=cdp_data,
        changed=False,
        host=task.host)
