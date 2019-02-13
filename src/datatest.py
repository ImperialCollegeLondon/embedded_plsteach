import smbus as sb
import time
import json
import paho.mqtt.client as mqtt
import ast
import socket

print("waiting for 10 s...")                                                                    #on start up wait for internet
time.sleep(10)
port_no = 1883                                                                                  #mqtt configurations, if encryption needed port = 8884
host = "ee-estott-octo.ee.ic.ac.uk"

client = mqtt.Client()
#client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")       #uncomment if need encryption
print("before connect")
while 1:
	try:                                                                                    #try reconnecting if connection failed
		client.connect(host, port = port_no)
	except socket.gaierror:
		print("trying to reconnect...")
		time.sleep(5)
		continue
	break

print("after connect")
client.publish("IC.embedded/plzteach/on", "ready")                                              #acknowledge pi connected                                

def on_message(client, userdata, message) :                                                     #on receiving message, check message content to set flags/configure sensors
	global loop_flag
	if loop_flag == True:
		if isinstance(ast.literal_eval((message.payload).decode('utf-8')), list):       #get configuration data from server
			global setup
			setup = (message.payload).decode('utf-8')
			loop_flag = False

	global pause                                                                            #on pause saves time and continue on unpause
	if (message.payload).decode('utf-8') == "pause":
		pause = True
		print("paused")
	if (message.payload).decode('utf-8') == "unpause":
		pause = False
	global stop                                                                             #on stop resets time to 0 and requires configuration again
	if (message.payload).decode('utf-8') == "stop":
		stop = True
		pause = True
	print((message.payload).decode('utf-8'))
	
client.on_message = on_message
client.subscribe("IC.embedded/plzteach/config")
client.loop_start()


while 1:
	pause = True
	stop = False
	loop_flag = True
	while loop_flag == True:
		print("waiting")
		time.sleep(10)

	ADDR = 0x48
	CONFIG_REG_1 = ast.literal_eval(setup)
	client.publish("IC.embedded/plzteach/on", "configured")
	print("configured")
	bus = sb.SMBus(1)
	pause_time = 0
	real_time = 0

	while stop == False:                                                                    #flags used to control pause and stop
		begin = time.perf_counter()
		while pause == False:
			for sensor in CONFIG_REG_1:                                             #send sensor data
				bus.write_i2c_block_data(ADDR, 1, sensor)
				data = bus.read_i2c_block_data(ADDR, 0 ,2)
				result = int.from_bytes(data, 'big')
				real_time = time.perf_counter() - begin - pause_time            #keep tracks of time when paused
				payload=json.dumps({'time':real_time,hex(sensor[0]):result})
				client.publish("IC.embedded/plzteach/result", payload)
				print(payload)
		pause_time = time.perf_counter() - begin - real_time
	client.publish("IC.embedded/plzteach/on", "stopped")

client.loop_stop()
