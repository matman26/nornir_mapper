from nornir_csv.plugins.inventory import CsvInventory
from plugins.tasks.cdp_map import map_neighbors
from nornir.core.inventory import Host
from nornir_utils.plugins.functions import print_result
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir import InitNornir
from tqdm import tqdm

InventoryPluginRegister.register("CsvInventoryPlugin", CsvInventory)

nr = InitNornir(inventory={'plugin': 'CsvInventoryPlugin', 'options': {'inventory_dir_path' : './inventory/'} },
                runner={'plugin': 'threaded','options': {'num_workers': 20}})

current_inventory_len = len(nr.inventory.hosts)
new_inventory_len = 0

while current_inventory_len != new_inventory_len:
    current_inventory_len = len(nr.inventory.hosts)
    stage = 1
    results = nr.run(
        task=map_neighbors)

    for host, result in tqdm(results.items(), desc=f"Mapping Topology"):
        for neighbor, data in result.result.items():
            shortname=neighbor.split('.')[0]
            if shortname not in nr.inventory.hosts:
                nr.inventory.hosts[shortname] = Host(name=shortname, platform='cisco_ios',
                                                    hostname=data['neighbor_address'],
                                                    username='cisco', password='cisco',
                                                    port=22)
            else:
                pass
    stage = stage + 1
    new_inventory_len = len(nr.inventory.hosts)

print(f"Done Mapping Topology. Found {new_inventory_len} devices in total.")
CsvInventory.write(dest_file='inventory/hosts.csv',inventory=nr.inventory)
print("Inventory Updated")



#print_result(results)

