import ssl
import json
from dotenv import load_dotenv
import time
import os
import paho.mqtt.client as mqtt
import mqtt_callbacks
import board
import adafruit_veml7700
import adafruit_shtc3

# import alarm

i2cl = board.I2C()
i2ct = board.I2C()
veml7700 = adafruit_veml7700.VEML7700(i2cl)
sht = adafruit_shtc3.SHTC3(i2ct)

load_dotenv()

USE_DEEP_SLEEP = True
PUBLISH_DELAY = 60

broker = os.getenv("MQTT_BROKER")
port = 1883
topic = "indoor/status"
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(username, password)
mqttc.on_connect = mqtt_callbacks.on_connect
mqttc.on_message = mqtt_callbacks.on_message
mqttc.on_subscribe = mqtt_callbacks.on_subscribe
# mqttc.on_unsubscribe = mqtt_callbacks.on_unsubscribe
mqttc.on_publish = mqtt_callbacks.on_publish

mqttc.user_data_set([])
mqttc.connect(broker, port, 60)
mqttc.loop_start()

try:
    while True:
        temperature, relative_humidity = sht.measurements
        light_level = veml7700.light
        whitebalance = veml7700.white
        lux_level = veml7700.lux
        temp = (temperature * (9 / 5)) + 32
        temp = round(temp, 2)
        relative_humidity = round(relative_humidity, 2)
        light_level = round(light_level, 2)
        whitebalance = round(whitebalance, 2)
        lux_level = round(lux_level, 2)
        # data = {
        #    "Temperature": temp,
        #    "Humidity": relative_humidity,
        #    "White light": whitebalance,
        #    "Ambient light": light_level,
        #    "Lux": lux_level,
        # }
        data = {
            "data": {
                "Climate": [
                    {"specie": "Temperature", "value": temp, "unit": "Fahrenheit"},
                    {"specie": "Humidity", "value": relative_humidity, "unit": "%"},
                ],
                "light": [
                    {"specie": "Ambient Light", "value": light_level, "unit": ""},
                    {"specie": "Lux", "value": lux_level, "unit": "lx"},
                    {"specie": "White Balance", "value": whitebalance, "unit": "K"},
                ],
            }
        }
        MQTT_MSG = json.dumps(data)
        if veml7700.light is None:
            print("Light sensor not detected")
        else:
            mqttc.publish(topic, MQTT_MSG)
        time.sleep(5)  # Send every 5 seconds
        # if USE_DEEP_SLEEP:
        #    mqttc.disconnect()
        #    pause = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + PUBLISH_DELAY)
        #    alarm.exit_and_deep_sleep_until_alarms(pause)
        # else:
        #    last_update = time.monotonic()
        # while time.monotonic() < last_update + PUBLISH_DELAY:
        #    mqtt_client.loop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()
