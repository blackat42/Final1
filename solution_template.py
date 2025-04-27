import network
import time
import ujson
from umqtt.simple import MQTTClient
import machine
import random  # Giả lập dữ liệu cảm biến

THINGSBOARD_HOST = 'app.coreiot.io'  # Hoặc địa chỉ server của bạn
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''

# Danh sách các thiết bị với access token
DEVICES_INFO = [
    {'access_token': 'uW2CtdjGE20NzJrIuvRN'},  # Device 1
    {'access_token': 'pDLvQ3j3QV3E9q8Sy9RG'},  # Device 2
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

def create_client(device_id, access_token):
    client = MQTTClient(f'DEVICE_{device_id}', THINGSBOARD_HOST, user=access_token, password='')
    return client

def setup_clients():
    for device_id, device in enumerate(DEVICES_INFO):
        client = create_client(device_id, device['access_token'])
        client.connect()
        print(f"[Device {device_id}] Connected and ready.")
        clients.append(client)

def read_temperature():
    # Giả lập đọc nhiệt độ
    return round(20 + random.uniform(-15, 15), 2)

def read_humidity():
    # Giả lập đọc độ ẩm
    return round(50 + random.uniform(-10, 10), 2)

def publish_telemetry():
    for device_id, device in enumerate(DEVICES_INFO):
        temperature = read_temperature()
        humidity = read_humidity()
        telemetry = {
            "temperature": temperature,
            "humidity": humidity
        }
        clients[device_id].publish('v1/devices/me/telemetry', ujson.dumps(telemetry))
        print(f"[Device {device_id}] Published telemetry: {telemetry}")

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
