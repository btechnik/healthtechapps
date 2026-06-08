"""Generate switch configurations for the cardiology clinic network."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def create_template_env(templates_dir="templates"):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

def generate_clinic_config(inventory_data, templates_dir="templates"):
    env = create_template_env(templates_dir)
    config_sections = []

    template_names = ["vlans.j2", "port_config.j2"]

    for template_name in template_names:
        try:
            template = env.get_template(template_name)
            rendered = template.render(**inventory_data)
            config_sections.append(rendered)
        except TemplateNotFound:
            print(f"  Warning: Template '{template_name}' not found, skipping.")

    return "\n".join(config_sections)

def generate_and_save(inventory_data, templates_dir="templates", output_dir="output"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    hostname = inventory_data["switch"]["hostname"]
    print(f"Generating config for {hostname}...")
    print(f"  Clinic: {inventory_data['clinic']['name']}")
    print(f"  Workstations: {len(inventory_data['workstations'])}")

    config = generate_clinic_config(inventory_data, templates_dir)

    config_file = output_path / f"{hostname}.cfg"
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(config)

    print(f"  Saved to {config_file}")
    print(f"  Config size: {len(config.splitlines())} lines")

    return config


if __name__ == "__main__":
    from inventory_loader import load_inventory

    data = load_inventory("inventory/clinic_network.yaml")
    config = generate_and_save(data)
    print("\nGenerated config preview (first 30 lines):")
    print("-" * 50)
    for line in config.splitlines()[:30]:
        print(line)