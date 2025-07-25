import json
import yaml

# Load your Home Assistant MQTT discovery dump
with open("mqtt-discovery-dump.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

entities = raw["data"]["device"]["entities"]

# Group by categories
views = {
    "Toon": [],
    "Gags": [],
    "Cog Suits": [],
    "Tasks": [],
    "Beans & Economy": [],
    "SOS & Rewards": [],
    "Unites": [],
    "Remotes": [],
    "Summons": [],
}

# Mapping keywords to views
categories = {
    "laff": "Toon",
    "district": "Toon",
    "zone": "Toon",
    "toon": "Toon",
    "wallet": "Beans & Economy",
    "bank": "Beans & Economy",
    "bean": "Beans & Economy",
    "gag": "Gags",
    "suit": "Cog Suits",
    "promotion": "Cog Suits",
    "task": "Tasks",
    "sos": "SOS & Rewards",
    "unites": "Unites",
    "remote": "Remotes",
    "pink": "Remotes",
    "summon": "Summons",
}

for e in entities:
    eid = e["entity_id"]
    assigned = False
    for key, view in categories.items():
        if key in eid.lower():
            views[view].append(eid)
            assigned = True
            break
    if not assigned:
        views["Toon"].append(eid)  # default fallback

# Create Lovelace YAML
dashboard_yaml = []
for title, entity_ids in views.items():
    if not entity_ids:
        continue
    dashboard_yaml.append({
        "title": title,
        "path": title.lower().replace(" ", "_"),
        "cards": [
            {
                "type": "entities",
                "title": title,
                "entities": entity_ids
            }
        ]
    })

# Save it
with open("toontown_dashboard.yaml", "w", encoding="utf-8") as f:
    yaml.dump(dashboard_yaml, f, sort_keys=False)

print("✅ Dashboard saved as toontown_dashboard.yaml")
