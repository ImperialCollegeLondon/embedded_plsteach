import paho.mqtt.client as mqtt

port_no = 8884
test_msg = "hello test from pi"

client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")

client.connect("test.mosquitto.org", port = port_no)

client.publish("IC.embedded/plzteach/test", "hi from pi")

