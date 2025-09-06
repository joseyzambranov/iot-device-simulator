import os
import time
import json
import random
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from threading import Thread

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

class IoTDevice:
    def __init__(self, device_id, device_type, security_level="normal"):
        self.device_id = device_id
        self.device_type = device_type
        self.security_level = security_level
        self.is_compromised = False
        
    def generate_data(self):
        base_data = {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": int(time.time()),
            "security_level": self.security_level
        }
        
        if self.device_type == "temperature_sensor":
            temp = 22 + random.uniform(-3, 3)
            if self.is_compromised:
                temp = random.uniform(50, 80)  # Anomalía
            base_data.update({
                "temperature": round(temp, 2),
                "humidity": random.uniform(30, 70)
            })
            
        elif self.device_type == "security_camera":
            base_data.update({
                "motion_detected": random.choice([True, False]),
                "recording": True,
                "battery_level": random.uniform(20, 100) if not self.is_compromised else 5
            })
            
        elif self.device_type == "smart_lock":
            base_data.update({
                "locked": random.choice([True, True, True, False]),  # Mostly locked
                "access_attempts": 1 if not self.is_compromised else random.randint(5, 20),
                "signal_strength": random.uniform(70, 100)
            })
            
        return base_data
    
    def simulate_attack(self):
        """Simula un dispositivo comprometido"""
        self.is_compromised = True
        print(f"⚠️ DISPOSITIVO COMPROMETIDO: {self.device_id}")

# Crear dispositivos simulados
devices = [
    IoTDevice("temp_01", "temperature_sensor", "low"),
    IoTDevice("cam_01", "security_camera", "normal"),
    IoTDevice("lock_01", "smart_lock", "high"),
    IoTDevice("temp_02", "temperature_sensor", "normal")
]

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Conectado al broker con código:", reason_code)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())
        if command.get("action") == "alarm":
            print("🔥 Alarma activada por el broker!")
        elif command.get("action") == "attack":
            # Simular ataque en dispositivo aleatorio
            device = random.choice(devices)
            device.simulate_attack()
    except:
        pass

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)

def send_device_data():
    while True:
        for device in devices:
            data = device.generate_data()
            payload = json.dumps(data)
            client.publish(MQTT_TOPIC, payload)
            print(f"📤 {device.device_id}: {payload}")
            
        # Ocasionalmente simular anomalías
        if random.random() < 0.1:  # 10% probabilidad
            random_device = random.choice(devices)
            if not random_device.is_compromised:
                random_device.simulate_attack()
                
        time.sleep(random.uniform(3, 7))  # Intervalo variable

Thread(target=send_device_data, daemon=True).start()

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nEjecución interrumpida por el usuario. Cerrando cliente MQTT...")
    client.disconnect()
