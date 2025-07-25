import json
import time
import random
import paho.mqtt.client as mqtt
import requests
import re

import mySecrets  # contains: haAddress, username, password

MQTT_BASE = "homeassistant"
TOON_API_PORT = 1547
POLL_INTERVAL = 10  # seconds

NUM_TOONS = 1

random_id = str(random.randint(0, 99999))
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ttr-ha-" + random_id)
client.username_pw_set(mySecrets.username, mySecrets.password)

def on_connect(client, userdata, flags, rc, props=None):
    print("MQTT connected with result code " + str(rc))

client.on_connect = on_connect
client.connect(mySecrets.haAddress, 1883)
client.loop_start()

def load_data(port:int):
    try:
        r = requests.get(f"http://localhost:{port}/all.json", headers={
            "Authorization": "Bearer ttr-local-ha",
            "User-Agent": "ttr-local-ha"
        })
        return r.json() if r.status_code == 200 else None
    except:
        return None


def clean_string(s):
    return re.sub(r'[\x00-\x1F\x7F]', '', s)

def safe_name(name):
    return clean_string(name.lower().replace(" ", "_").replace(".",""))

def publish_sensor(unique_id, name, value, unit=None, icon=None, value_template=None):
    sensor_topic = f"{MQTT_BASE}/sensor/{unique_id}"
    state_topic = f"{sensor_topic}/state"
    config_topic = f"{sensor_topic}/config"

    config = {
        "name": name,
        "state_topic": state_topic,
        "unique_id": unique_id,
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        }
    }
    if unit: config["unit_of_measurement"] = unit
    if icon: config["icon"] = icon
    if value_template: config["value_template"] = value_template

    client.publish(config_topic, json.dumps(config), retain=True)
    client.publish(state_topic, value, retain=True)

def publish_discovery(toon_data):
    laff = toon_data["laff"]
    gags = toon_data["gags"]
    suits = toon_data["cogsuits"]
    location = toon_data["location"]

    laff_sensor_id = f"{safe_name(toon_name)}_laff"
    laff_config = {
        "name": "Laff",
        "state_topic": f"{MQTT_BASE}/sensor/{laff_sensor_id}/state",
        "json_attributes_topic": f"{MQTT_BASE}/sensor/{laff_sensor_id}/attributes",
        "unique_id": laff_sensor_id,
        "unit_of_measurement": "Laff",
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        },
        "icon": "mdi:heart"
    }
    laff_attrs = {
        "max": laff.get("max")
    }

    client.publish(f"{MQTT_BASE}/sensor/{laff_sensor_id}/config", json.dumps(laff_config), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{laff_sensor_id}/state", laff["current"], retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{laff_sensor_id}/attributes", json.dumps(laff_attrs), retain=True)


    # Location
    publish_sensor(f"{safe_name(toon_name)}_district", "Location District", location["district"])
    publish_sensor(f"{safe_name(toon_name)}_zone", "Location Zone", location["zone"])

        # Toon Info
    toon = toon_data["toon"]
    toon_sensor_id = f"{safe_name(toon_name)}_toon"
    toon_config = {
        "name": "Toon",
        "state_topic": f"{MQTT_BASE}/sensor/{toon_sensor_id}/state",
        "json_attributes_topic": f"{MQTT_BASE}/sensor/{toon_sensor_id}/attributes",
        "unique_id": toon_sensor_id,
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        },
        "icon": "mdi:account"
    }
    toon_attrs = {
        "species": toon.get("species"),
        "head_color": toon.get("headColor"),
        "style": toon.get("style"),
        "id": toon.get("id")
    }
    client.publish(f"{MQTT_BASE}/sensor/{toon_sensor_id}/config", json.dumps(toon_config), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{toon_sensor_id}/state", toon_name, retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{toon_sensor_id}/attributes", json.dumps(toon_attrs), retain=True)


    # Gag Tracks - 1 sensor per gag track
    for track, gag_info in gags.items():
        track_id = f"{safe_name(toon_name)}_{track.lower()}_gag"
        sensor_name = f"Gag {track}"

        if gag_info is None:
            # No gag track — create sensor with "{track}less"
            config = {
                "name": sensor_name,
                "state_topic": f"{MQTT_BASE}/sensor/{track_id}/state",
                "unique_id": track_id,
                "device": {
                    "name": toon_name,
                    "identifiers": [f"ttr_{safe_name(toon_name)}"]
                },
                "icon": "mdi:cancel"
            }
            state = f"{track}less"
            client.publish(f"{MQTT_BASE}/sensor/{track_id}/config", json.dumps(config), retain=True)
            client.publish(f"{MQTT_BASE}/sensor/{track_id}/state", state, retain=True)
        else:
            gag = gag_info["gag"]
            name = gag.get("name", "Unknown")
            level = gag.get("level", None)
            exp = gag_info.get("experience", {}).get("current", None)
            exp_next = gag_info.get("experience", {}).get("next", None)
            organic = gag_info.get("organic", None)
            is_organic = organic is not None

            attributes = {
                "track": track,
                "level": level,
                "exp": exp,
                "exp_next": exp_next,
                "organic": is_organic,
                "organic_level": organic["level"] if is_organic else None,
                "organic_name": organic["name"] if is_organic else None,
            }

            config = {
                "name": sensor_name,
                "state_topic": f"{MQTT_BASE}/sensor/{track_id}/state",
                "json_attributes_topic": f"{MQTT_BASE}/sensor/{track_id}/attributes",
                "unique_id": track_id,
                "device": {
                    "name": toon_name,
                    "identifiers": [f"ttr_{safe_name(toon_name)}"]
                },
                "icon": "mdi:party-popper"
            }

            client.publish(f"{MQTT_BASE}/sensor/{track_id}/config", json.dumps(config), retain=True)
            client.publish(f"{MQTT_BASE}/sensor/{track_id}/state", name, retain=True)
            client.publish(f"{MQTT_BASE}/sensor/{track_id}/attributes", json.dumps(attributes), retain=True)



       # Cog Suits - 2 sensors per department
    for short, suit in suits.items():
        dept = suit["department"]
        dept_id = safe_name(dept)
        suit_name = clean_string(suit["suit"].get("name", "Unknown"))
        level = suit.get("level")
        version = suit.get("version")
        current = suit["promotion"]["current"]
        target = suit["promotion"]["target"]

        # Suit sensor
        suit_sensor_id = f"{safe_name(toon_name)}_{dept_id}_suit"
        suit_config = {
            "name": f"Suit {dept}",
            "state_topic": f"{MQTT_BASE}/sensor/{suit_sensor_id}/state",
            "json_attributes_topic": f"{MQTT_BASE}/sensor/{suit_sensor_id}/attributes",
            "unique_id": suit_sensor_id,
            "device": {
                "name": toon_name,
                "identifiers": [f"ttr_{safe_name(toon_name)}"]
            },
            "icon": "mdi:robot"
        }
        suit_attrs = {
            "level": level,
            "version": version
        }

        client.publish(f"{MQTT_BASE}/sensor/{suit_sensor_id}/config", json.dumps(suit_config), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{suit_sensor_id}/state", suit_name, retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{suit_sensor_id}/attributes", json.dumps(suit_attrs), retain=True)

        # Promotion sensor
        promo_sensor_id = f"{safe_name(toon_name)}_{dept_id}_promotion"
        promo_config = {
            "name": f"Promotion {dept}",
            "state_topic": f"{MQTT_BASE}/sensor/{promo_sensor_id}/state",
            "json_attributes_topic": f"{MQTT_BASE}/sensor/{promo_sensor_id}/attributes",
            "unique_id": promo_sensor_id,
            "unit_of_measurement": "XP",
            "device": {
                "name": toon_name,
                "identifiers": [f"ttr_{safe_name(toon_name)}"]
            },
            "icon": "mdi:chart-bar"
        }

        promo_attrs = {
            "target": target
        }

        client.publish(f"{MQTT_BASE}/sensor/{promo_sensor_id}/config", json.dumps(promo_config), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{promo_sensor_id}/state", current, retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{promo_sensor_id}/attributes", json.dumps(promo_attrs), retain=True)

    # Tasks - one sensor per active task
    tasks = toon_data.get("tasks", [])
    for idx, task in enumerate(tasks):
        obj = task["objective"]
        progress = obj.get("progress", {})
        from_name = task["from"].get("name", "Unknown")
        to_name = task["to"].get("name", "Unknown")
        where = obj.get("where", "")
        reward = task.get("reward", "")
        deletable = task.get("deletable", False)
        task_type = task.get("type", "")

        # Build state
        state_text = obj.get("text", "Unknown Objective")
        if where and where.lower() != "anywhere":
            state_text += f" in {where}"

        sensor_id = f"{safe_name(toon_name)}_task_{idx + 1}"
        config = {
            "name": f"Task {idx + 1}",
            "state_topic": f"{MQTT_BASE}/sensor/{sensor_id}/state",
            "json_attributes_topic": f"{MQTT_BASE}/sensor/{sensor_id}/attributes",
            "unique_id": sensor_id,
            "device": {
                "name": toon_name,
                "identifiers": [f"ttr_{safe_name(toon_name)}"]
            },
            "icon": "mdi:check-circle-outline"
        }

        attributes = {
            "current": progress.get("current", 0),
            "target": progress.get("target", 0),
            "from_name": from_name,
            "to_name": to_name,
            "reward": reward,
            "deletable": deletable,
            "type" : task_type
        }

        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/config", json.dumps(config), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/state", state_text, retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/attributes", json.dumps(attributes), retain=True)


            # Beans Wallet
    beans = toon_data.get("beans", {})
    jar = beans.get("jar", {})
    bank = beans.get("bank", {})

    # Wallet
    wallet_sensor_id = f"{safe_name(toon_name)}_beans_wallet"
    wallet_config = {
        "name": "Beans Wallet",
        "state_topic": f"{MQTT_BASE}/sensor/{wallet_sensor_id}/state",
        "json_attributes_topic": f"{MQTT_BASE}/sensor/{wallet_sensor_id}/attributes",
        "unique_id": wallet_sensor_id,
        "unit_of_measurement": "Beans",
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        },
        "icon": "mdi:wallet"
    }
    wallet_attrs = {
        "max": jar.get("max", 0)
    }
    client.publish(f"{MQTT_BASE}/sensor/{wallet_sensor_id}/config", json.dumps(wallet_config), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{wallet_sensor_id}/state", jar.get("current", 0), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{wallet_sensor_id}/attributes", json.dumps(wallet_attrs), retain=True)

    # Bank
    bank_sensor_id = f"{safe_name(toon_name)}_beans_bank"
    bank_config = {
        "name": "Beans Bank",
        "state_topic": f"{MQTT_BASE}/sensor/{bank_sensor_id}/state",
        "json_attributes_topic": f"{MQTT_BASE}/sensor/{bank_sensor_id}/attributes",
        "unique_id": bank_sensor_id,
        "unit_of_measurement": "Beans",
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        },
        "icon": "mdi:bank"
    }
    bank_attrs = {
        "max": bank.get("max", 0)
    }
    client.publish(f"{MQTT_BASE}/sensor/{bank_sensor_id}/config", json.dumps(bank_config), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{bank_sensor_id}/state", bank.get("current", 0), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{bank_sensor_id}/attributes", json.dumps(bank_attrs), retain=True)

    # SOS Cards
    rewards = toon_data.get("rewards",{})
    soses = rewards.get("sos", {})
    for sos_name, count in soses.items():
        sos_id = f"{safe_name(toon_name)}_sos_{safe_name(sos_name)}"
        sos_config = {
            "name": f"SOS {sos_name}",
            "state_topic": f"{MQTT_BASE}/sensor/{sos_id}/state",
            "unique_id": sos_id,
            "unit_of_measurement": "Cards",
            "device": {
                "name": toon_name,
                "identifiers": [f"ttr_{safe_name(toon_name)}"]
            },
            "icon": "mdi:cards-playing"
        }

        client.publish(f"{MQTT_BASE}/sensor/{sos_id}/config", json.dumps(sos_config), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{sos_id}/state", count, retain=True)

    # Unites
    unites = rewards.get("unites", {})
    for category, entries in unites.items():
        for unite_type, count in entries.items():
            sensor_id = f"{safe_name(toon_name)}_unites_{safe_name(category)}_{safe_name(unite_type)}"
            unite_str = unite_type.replace(category, "")
            config = {
                "name": f"Unites {category} {unite_str}",
                "state_topic": f"{MQTT_BASE}/sensor/{sensor_id}/state",
                "unique_id": sensor_id,
                "unit_of_measurement": "Unites",
                "device": {
                    "name": toon_name,
                    "identifiers": [f"ttr_{safe_name(toon_name)}"]
                },
                "icon": "mdi:cards"
            }

            client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/config", json.dumps(config), retain=True)
            client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/state", count, retain=True)

    # Pink Slips
    pink_slips = rewards.get("pinkslips", 0)
    slip_id = f"{safe_name(toon_name)}_pinkslips"
    slip_config = {
        "name": "Pink Slips",
        "state_topic": f"{MQTT_BASE}/sensor/{slip_id}/state",
        "unique_id": slip_id,
        "unit_of_measurement": "Slips",
        "device": {
            "name": toon_name,
            "identifiers": [f"ttr_{safe_name(toon_name)}"]
        },
        "icon": "mdi:ticket-confirmation"
    }
    client.publish(f"{MQTT_BASE}/sensor/{slip_id}/config", json.dumps(slip_config), retain=True)
    client.publish(f"{MQTT_BASE}/sensor/{slip_id}/state", pink_slips, retain=True)

    # Remotes
    remotes = rewards.get("remotes", {})
    for remote_type, levels in remotes.items():
        for level, count in levels.items():
            remote_id = f"{safe_name(toon_name)}_remotes_{safe_name(remote_type)}_{level}"
            remote_config = {
                "name": f"{remote_type} Level {level}",
                "state_topic": f"{MQTT_BASE}/sensor/{remote_id}/state",
                "unique_id": remote_id,
                "unit_of_measurement": "Remotes",
                "device": {
                    "name": toon_name,
                    "identifiers": [f"ttr_{safe_name(toon_name)}"]
                },
                "icon": "mdi:remote"
            }
            client.publish(f"{MQTT_BASE}/sensor/{remote_id}/config", json.dumps(remote_config), retain=True)
            client.publish(f"{MQTT_BASE}/sensor/{remote_id}/state", count, retain=True)

    # Summons
    summons = rewards.get("summons", {})
    for summon_info in summons.values():
        cog_name = summon_info.get("name", "Unknown")
        sensor_id = f"{safe_name(toon_name)}_summons_{safe_name(cog_name)}"

        # Only check real flags, ignore 'name'
        has_any = any(summon_info.get(key, False) for key in ("single", "building", "invasion"))

        config = {
            "name": f"Summons {clean_string(cog_name)}",
            "state_topic": f"{MQTT_BASE}/sensor/{sensor_id}/state",
            "json_attributes_topic": f"{MQTT_BASE}/sensor/{sensor_id}/attributes",
            "unique_id": sensor_id,
            "device": {
                "name": toon_name,
                "identifiers": [f"ttr_{safe_name(toon_name)}"]
            },
            "icon": "mdi:bullhorn"
        }

        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/config", json.dumps(config), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/state", str(has_any).lower(), retain=True)
        client.publish(f"{MQTT_BASE}/sensor/{sensor_id}/attributes", json.dumps(summon_info), retain=True)




def publish_all_state(toon_data):
    # This lets you just dump the JSON if you want
    state_topic = f"sensor/{safe_name(toon_name)}"
    client.publish(state_topic, json.dumps(toon_data), retain=True)


# Main loop
while True:
    for i in range(NUM_TOONS):
        port = TOON_API_PORT + i
        toon_data = load_data(port)

        if toon_data:
            toon_name = toon_data["toon"]["name"]
            publish_all_state(toon_data)
            publish_discovery(toon_data)
            print(f"Published for {toon_name} on port {port}")
        else:
            print(f"No toon data found on port {port}.")

    time.sleep(POLL_INTERVAL)
