import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect("test.mosquitto.org",port=1883)

def on_message(client, userdata, message) :
	print("Received message:{} on topic {}".format(message.payload, message.topic))

client.on_message = on_message
client.subscribe("IC.embedded/plzteach/#")
client.loop_start() 

#to stop loop
#client.loop_stop()
