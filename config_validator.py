"""Validate clinic switch configurations against healthcare security rules."""


FORBIDDEN_COMMANDS = [
    "permit any any",
    "no switchport port-security",
    "switchport mode trunk",
]

REQUIRED_PATTERNS = [
    "switchport port-security",
    "switchport port-security violation shutdown",
    "spanning-tree portfast",
    "no shutdown",
]


def validate_config(config_text, clinic_name):
    results = []

    # Check that no forbidden commands exist in the config
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in config_text:
            results.append({"rule": f"No '{forbidden}' allowed", "status": "FAIL", "message": f"Found insecure command that could expose patient data", "severity": "CRITICAL"})
        else:
            results.append({"rule": f"No '{forbidden}' allowed", "status": "PASS", "message": "Not found in config", "severity": "CRITICAL"})

    # Check that all required security patterns are present
    for pattern in REQUIRED_PATTERNS:
        if pattern in config_text:
            results.append({"rule": f"Required: '{pattern}'", "status": "PASS", "message": "Found in config", "severity": "HIGH"})
        else:
            results.append({"rule": f"Required: '{pattern}'", "status": "FAIL", "message": "Missing required security control", "severity": "HIGH"})

    # Verify VLAN segmentation between admin and clinical traffic
    if "vlan 10" in config_text and "vlan 20" in config_text:
        results.append({"rule": "VLAN segmentation defined", "status": "PASS", "message": "Admin (VLAN 10) and Clinical (VLAN 20) VLANs present", "severity": "CRITICAL"})
    else:
        results.append({"rule": "VLAN segmentation defined", "status": "FAIL", "message": "Missing VLAN segmentation between admin and clinical traffic", "severity": "CRITICAL"})

    # Verify unused ports are shut down to prevent unauthorized access
    if "shutdown" in config_text and "UNUSED" in config_text:
        results.append({"rule": "Unused ports disabled", "status": "PASS", "message": "Unused ports are shut down", "severity": "HIGH"})
    else:
        results.append({"rule": "Unused ports disabled", "status": "FAIL", "message": "Unused ports should be disabled to prevent unauthorized access", "severity": "HIGH"})

    # Verify the config is not empty
    if len(config_text.strip()) == 0:
        results.append({"rule": "Config not empty", "status": "FAIL", "message": "Generated config is empty", "severity": "CRITICAL"})
    else:
        results.append({"rule": "Config not empty", "status": "PASS", "message": f"Config has {len(config_text.splitlines())} lines", "severity": "INFO"})

    passed = all(r["status"] == "PASS" for r in results)
    return {"passed": passed, "results": results, "clinic": clinic_name}