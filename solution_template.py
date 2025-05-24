import network
import time
import ujson
from umqtt.simple import MQTTClient
import machine
import random

THINGSBOARD_HOST = 'app.coreiot.io'
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''

# Danh sách các thiết bị với access token
DEVICES_INFO = [
    {
        'name': 'Sensor C1',
        'client_id': 'your_id',
        'username': 'your_username',
        'password': 'your_password'
    },
]


clients = []

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected to WiFi!")

def create_client(client_id, username, password):
    client = MQTTClient(client_id, THINGSBOARD_HOST, user=username, password=password)
    return client

def setup_clients():
    for device in DEVICES_INFO:
        print(device['client_id'], device['username'], device['password'])
        client = create_client(device['client_id'], device['username'], device['password'])
        client.connect()
        print(f"[{device['name']}] Connected and ready.")
        clients.append(client)


def read_temperature():
    # Giả lập đọc nhiệt độ
    return round(20 + random.uniform(-15, 15), 2)

def read_humidity():
    # Giả lập đọc độ ẩm
    return round(50 + random.uniform(-10, 10), 2)

def publish_telemetry():
    for device, client in zip(DEVICES_INFO, clients):
        temperature = read_temperature()
        humidity = read_humidity()
        telemetry = {
            "temperature": temperature,
            "humidity": humidity
        }
        client.publish('esp/telemetry', ujson.dumps(telemetry))
        print(f"[{device['name']}] Published telemetry: {telemetry}")

# Kết nối WiFi
connect_wifi()

# Khởi tạo các MQTT clients
setup_clients()

# Vòng lặp chính
try:
    while True:
        publish_telemetry()
        time.sleep(5)  # Gửi dữ liệu mỗi 5 giây

except KeyboardInterrupt:
    print("Disconnecting...")
    for client in clients:
        client.disconnect()
