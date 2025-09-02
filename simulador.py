import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Cargar variables del .env
load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Conectado al broker con código: " + str(reason_code))
    client.subscribe(MQTT_TOPIC)

# Callback cuando llega un mensaje
def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")

# Crear cliente MQTT
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Conectar con el broker
client.connect(MQTT_HOST, MQTT_PORT, 60)

# Publicar un mensaje de prueba
client.publish(MQTT_TOPIC, "Hola IoT desde Python con .env!")

# Mantener el cliente escuchando
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nEjecución interrumpida por el usuario. Cerrando cliente MQTT...")
    client.disconnect()
