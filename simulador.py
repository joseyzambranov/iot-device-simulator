import os
import time
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from threading import Thread

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
DEVICE_ID = os.getenv("DEVICE_ID")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Conectado al broker con código:", reason_code)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())
        if command.get("action") == "alarm":
            print("🔥 Alarma activada por el broker!")
    except:
        pass

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)

def send_sensor_data():
    while True:
        data = {
            "device_id": DEVICE_ID,
            "timestamp": int(time.time()),
            "temperature": 20 + 5 * (time.time() % 10) / 10,
            "motion_detected": False
        }
        payload = json.dumps(data)
        client.publish(MQTT_TOPIC, payload)
        print(f"Mensaje enviado: {payload}")
        time.sleep(5)

Thread(target=send_sensor_data, daemon=True).start()

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nEjecución interrumpida por el usuario. Cerrando cliente MQTT...")
    client.disconnect()
