import smbus as sb

ADDR = 0x48
CONFIG_REG_1 = [0xC3, 0xE3]
bus = sb.SMBus(1)

def get_nconversion(config, N):
	for x in range(N):
		bus.write_i2c_block_data(ADDR, 1, config)
		data = bus.read_i2c_block_data(ADDR, 0 ,2)
		print(int.from_bytes(data, 'big')/32768*4.096)
get_nconversion(CONFIG_REG_1, 5000)
