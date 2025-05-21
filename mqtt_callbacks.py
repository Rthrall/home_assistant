import json

topic = "indoor/status"

# MQTT_MSG = json.dumps(
#    {
#        "temperature": "NULL",
#        "humidity": "NULL",
#        "White light": "NULL",
#        "Ambient light": "NULL",
#        "Lux": "NULL",
#    }
# )

MQTT_MSG = json.dumps(
    {
        "data": {
            "Climate": [
                {"specie": "Temperature", "value": "0", "unit": "Fahrenheit"},
                {"specie": "Humidity", "value": "NULL", "unit": "%"},
            ],
            "light": [
                {"specie": "Ambient Light", "value": "NULL", "unit": ""},
                {"specie": "Lux", "value": "NULL", "unit": "lx"},
                {"specie": "White Balance", "value": "NULL0", "unit": "K"},
            ],
        }
    }
)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def on_publish(client, userdata, mid, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to publish: {reason_code}.")
    else:
        print(f"Message {mid} published")


def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()


def on_message(client, userdata, message):
    # userdata is the structure we choose to provide, here it's a list()
    userdata.append(message.payload)
    # We only want to process 10 messages
    if len(userdata) >= 10:
        client.unsubscribe("$SYS/#")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe(topic)
        client.publish(topic, MQTT_MSG)
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        #if int(MQTT_MSG["data"]["Climate"][0]["value"]) == int(0):
        #    print("Waiting for data...")
        #else:
        #    client.subscribe(topic)
        #    client.publish(topic, MQTT_MSG)
