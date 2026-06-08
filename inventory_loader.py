"""Load and validate the cardiology clinic network inventory."""

import sys
from pathlib import Path

import yaml


REQUIRED_SWITCH_FIELDS = ["hostname", "host", "device_type", "username", "password"]
REQUIRED_WORKSTATION_FIELDS = ["name", "port", "description", "vlan", "mac_limit"]

def load_inventory(inventory_path):
    path = Path(inventory_path)
    if not path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError("Inventory file is empty")

    validate_inventory(data)
    return data


def validate_inventory(data):
    if "switch" not in data:
        raise ValueError("Inventory must contain a 'switch' section")
    if "vlans" not in data:
        raise ValueError("Inventory must contain a 'vlans' section")
    if "workstations" not in data:
        raise ValueError("Inventory must contain a 'workstations' section")

    switch = data["switch"]
    missing = [f for f in REQUIRED_SWITCH_FIELDS if f not in switch]
    if missing:
        raise ValueError(f"Switch missing required fields: {', '.join(missing)}")

    for ws in data["workstations"]:
        missing = [f for f in REQUIRED_WORKSTATION_FIELDS if f not in ws]
        if missing:
            raise ValueError(
                f"Workstation '{ws.get('name', 'UNKNOWN')}' missing fields: "
                f"{', '.join(missing)}"
            )
        
if __name__ == "__main__":
    try:
        data = load_inventory("inventory/clinic_network.yaml")
        print(f"Clinic: {data['clinic']['name']}")
        print(f"Switch: {data['switch']['hostname']} ({data['switch']['host']})")
        print(f"VLANs: {len(data['vlans'])}")
        print(f"Workstations: {len(data['workstations'])}")
        for ws in data["workstations"]:
            print(f"  - {ws['name']} on {ws['port']} (VLAN {ws['vlan']})")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)