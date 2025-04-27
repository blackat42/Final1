import network
import time
import ujson
from umqtt.simple import MQTTClient
import machine

THINGSBOARD_HOST = 'app.coreiot.io'  # Or your server address
ACCESS_TOKEN = 'pp11caxojei2t9vq8iyx'
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''

led = machine.Pin(15, machine.Pin.OUT)

led_state = False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected to WiFi!")

def on_message(topic, msg):
    global led_state
    try:
        print(f"Received message on topic {topic}: {msg}")
        data = ujson.loads(msg)
        
        if data.get('method') == 'setLedState':
            # Update LED state
            led_state = data.get('params', False)
            led.value(led_state)  # Set LED on/off
            print(f"LED state updated to: {led_state}")
            
            # Prepare response
            response = {
                "newState": int(led_state)
            }
            
            # Extract request ID from topic
            request_id = topic.decode().split('/')[-1]
            response_topic = f'v1/devices/me/rpc/response/{request_id}'
            client.publish(response_topic, ujson.dumps(response))
            print(f"Published response to {response_topic}: {response}")
    
    except Exception as e:
        print(f"Error processing message: {e}")

# Connect to WiFi
connect_wifi()

# Setup MQTT client
client = MQTTClient('MYDEVICE', THINGSBOARD_HOST, user=ACCESS_TOKEN, password='')
client.set_callback(on_message)
client.connect()

# Subscribe to RPC requests
client.subscribe('v1/devices/me/rpc/request/+')
print("Subscribed to RPC requests...")

# Main loop
try:
    while True:
        client.check_msg()  # Non-blocking wait for messages
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Disconnected.")
    client.disconnect()
