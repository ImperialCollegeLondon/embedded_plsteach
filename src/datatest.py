import smbus as sb
import time
import json
import paho.mqtt.client as mqtt

port_no = 8884

client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")

client.connect("test.mosquitto.org", port = port_no)

ADDR = 0x48
CONFIG_REG_1 = [0xC3, 0xE3]
bus = sb.SMBus(1)

def get_nconversion(config, N):
	for x in range(N):
		bus.write_i2c_block_data(ADDR, 1, config)
		data = bus.read_i2c_block_data(ADDR, 0 ,2)
		result=int.from_bytes(data, 'big')/32768*4.096
		payload=json.dumps({'time':time.perf_counter(),'result':result})
		client.publish("IC.embedded/plzteach/test", payload)
		print(payload)
get_nconversion(CONFIG_REG_1, 5000)
