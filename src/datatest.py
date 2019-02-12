import smbus as sb
import time
import json
import paho.mqtt.client as mqtt
import ast

print("waiting for 3 s...")
time.sleep(3)
port_no = 8884


client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
print("before connect")
client.connect("test.mosquitto.org", port = port_no)
print("after connect")
client.publish("IC.embedded/plzteach/on", "I'M GOING IN")

def on_message(client, userdata, message) :
	global loop_flag
#       print("Received message:{} on topic {}".format(message.payload, message$
	global setup
	setup = (message.payload).decode('utf-8')
	print(setup)
	loop_flag = 0

client.on_message = on_message
client.subscribe("IC.embedded/plzteach/config")

while 1:
	loop_flag = 1
	client.loop_start()
	while loop_flag == 1:
		print("waiting")
		time.sleep(10)

	client.loop_stop()
	ADDR = 0x48
	CONFIG_REG_1 = ast.literal_eval(setup)
	bus = sb.SMBus(1)
	begin=time.perf_counter()

	def get_nconversion(config, N):
		for x in range(N):
			for sensor in config:
				bus.write_i2c_block_data(ADDR, 1, sensor)
				data = bus.read_i2c_block_data(ADDR, 0 ,2)
				result=int.from_bytes(data, 'big')/32768*4.096
				payload=json.dumps({'time':time.perf_counter()-begin,hex(sensor[0]):result})
				client.publish("IC.embedded/plzteach/result", payload)
				print(payload)

	get_nconversion(CONFIG_REG_1, 5000)

	client.publish("IC.embedded/plzteach/on", "done")

