# mqtt_handler.py
import paho.mqtt.client as paho
from paho import mqtt


# hivemq.webclient.1699615123087
# Hqd:<e;24G!I7wABkvL9
class MQTTHandler:
    def __init__(self, broker_address, port, topic, username=None, password=None):
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.username = username
        self.password = password
        self.client = paho.Client()

        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT broker")
            # Subscribe to the topic when connected
            self.client.subscribe(self.topic)
        elif rc == 1:
            print("Connection refused - incorrect protocol version")
        elif rc == 2:
            print("Connection refused - invalid client identifier")
        elif rc == 3:
            print("Connection refused - server unavailable")
        elif rc == 4:
            print("Connection refused - bad username or password")
        elif rc == 5:
            print("Connection refused - not authorized")
        else:
            print(f"Connection failed with result code {rc}")

    # def on_connect(self, client, userdata, flags, rc):
    #     if rc == 0:
    #         print("Connected to MQTT broker")
    #         # Subscribe to the topic when connected
    #         client.subscribe(self.topic)
    #     elif rc == 1:
    #         print("Connection refused - incorrect protocol version")
    #     elif rc == 2:
    #         print("Connection refused - invalid client identifier")
    #     elif rc == 3:
    #         print("Connection refused - server unavailable")
    #     elif rc == 4:
    #         print("Connection refused - bad username or password")
    #     elif rc == 5:
    #         print("Connection refused - not authorized")
    #     else:
    #         print(f"Connection failed with result code {rc}")

    def on_message(self, client, userdata, message, tmp=None):
        print(
            "Received message "
            + str(message.payload)
            + " on topic '"
            + message.topic
            + "' with QoS "
            + str(message.qos)
        )

    def connect(self):
        self.protocol = "paho.MQTTv5"
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        try:
            # Set username and password if provided
            if self.username and self.password:

                self.client.username_pw_set(self.username, self.password)

            # Connect to the MQTT broker
            self.client.connect(self.broker_address, self.port)

            # Start the MQTT loop
            self.client.loop_start()
        except ConnectionError as e:
            print(f"Error connecting to MQTT broker: {e}")

    def disconnect(self):
        # Disconnect from the MQTT broker
        self.client.disconnect()

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        print("Subscribed to topic!")
