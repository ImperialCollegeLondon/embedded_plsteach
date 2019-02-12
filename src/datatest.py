import smbus as sb
import time
import json
import paho.mqtt.client as mqtt
import ast

print("waiting for 10 s...")
time.sleep(10)
port_no = 8884

client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
print("before connect")
client.connect("test.mosquitto.org", port = port_no)
print("after connect")
client.publish("IC.embedded/plzteach/on", "ready")

def on_message(client, userdata, message) :
	global loop_flag
	loop_flag = False
	global pause
	if (message.payload).decode('utf-8') == "pause":
		pause = True
		print("paused")
	if (message.payload).decode('utf-8') == "unpause":
		pause = False
	global stop
	if (message.payload).decode('utf-8') == "stop":
		stop = True
		pause = True
	global setup
	setup = (message.payload).decode('utf-8')
	print(setup)
	

client.on_message = on_message
client.subscribe("IC.embedded/plzteach/config")
client.loop_start()

while 1:
	loop_flag = True
	pause = False
	stop = False
	while loop_flag == True:
		print("waiting")
		time.sleep(10)

	ADDR = 0x48
	CONFIG_REG_1 = ast.literal_eval(setup)
	bus = sb.SMBus(1)
	begin = time.perf_counter()
	pause_time = 0

	while stop == False:
		while pause == False:
			for sensor in CONFIG_REG_1:
				bus.write_i2c_block_data(ADDR, 1, sensor)
				data = bus.read_i2c_block_data(ADDR, 0 ,2)
				result = int.from_bytes(data, 'big')/32768*4.096
				global real_time
				real_time = time.perf_counter() - begin - pause_time
				payload=json.dumps({'time':real_time,hex(sensor[0]):result})
				client.publish("IC.embedded/plzteach/result", payload)
				print(payload)
		pause_time = time.perf_counter() - begin - real_time
	client.publish("IC.embedded/plzteach/on", "stopped")
	print("stopped")

client.loop_stop()
