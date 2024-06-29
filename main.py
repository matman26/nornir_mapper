from nornir_utils.plugins.functions import print_result
from plugins.tasks.cdp_map import map_neighbors
from nornir.core.inventory import Host
from N2G import drawio_diagram 
from nornir import InitNornir
from tqdm import tqdm

nr = InitNornir(
  inventory={
    'plugin': 'SimpleInventory', 
    'options': {
       'host_file' : './inventory/hosts.yaml'
    } 
  },
  runner={
    'plugin': 'threaded',
    'options': {
       'num_workers': 20
    }
  }
)

current_inventory_len = len(nr.inventory.hosts)
new_inventory_len = 0

while current_inventory_len != new_inventory_len:
    current_inventory_len = len(nr.inventory.hosts)
    stage = 1
    results = nr.run(task=map_neighbors)

    for host, result in tqdm(results.items(), desc=f"Mapping Topology"):
        for neighbor, data in result.result.items():
            shortname=neighbor.split('.')[0]
            # Populate the neighbor we just find in the inventory so that
            # we include that neighbor next iteration
            if shortname not in nr.inventory.hosts:
                nr.inventory.hosts[shortname] = Host(name=shortname, platform='cisco_ios',
                                                    hostname=data['neighbor_address'],
                                                    username='cisco', password='cisco',
                                                    port=22)

            # We also want to keep track of links to generate the diagram
            if 'neighbors' not in nr.inventory.hosts[shortname].data:
                 nr.inventory.hosts[shortname].data['neighbors'] = {}

	    # remote-local  are inverted because we are populating them from the
	    # neighbors perspective and not the current hosts perspective
            if host not in nr.inventory.hosts[shortname].data['neighbors']:
               nr.inventory.hosts[shortname].data['neighbors'][host] = {
                  'local-interface'  : data['remote_interface'],
  	          'remote-interface' : data['local_interface'],
	       }

    stage = stage + 1
    new_inventory_len = len(nr.inventory.hosts)

print(f"Done Mapping Topology. Found {new_inventory_len} devices in total.")
print("Inventory Updated")
print_result(results)

# Lets build a graph now!
diagram   = drawio_diagram() 
diag_name = "nornir_mapper_graph.drawio"

print(f"Building diagram...")
# This inserts a host and each of its N links.
inventory_list = []
for hostname, host in nr.inventory.hosts.items():
  for neighbor, info in host.data.get('neighbors', {}).items():
    inventory_list.append({
      "source"    : hostname,
      "src_label" : info['local-interface'],
      "target"    : neighbor,
      "trgt_label": info['remote-interface'],

    })

diagram.from_list(inventory_list)
diagram.dump_file(filename=diag_name, folder="./")
print(f"Done building diagram: {diag_name}")
