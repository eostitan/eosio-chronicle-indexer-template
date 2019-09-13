import os
import asyncio
import websockets
import time
import signal
import json
import traceback
from datetime import datetime
from debug_log import logger
import struct

# if config to save all data
ARCHIVE_MODE = os.getenv('ARCHIVE_MODE', 'OFF').upper()
if ARCHIVE_MODE != 'OFF':
	from storage import ArchiveStorage
	archive = ArchiveStorage()

# for gracefully handling docker signals
KEEP_RUNNING = True
def stop_container():
    global KEEP_RUNNING
    KEEP_RUNNING = False
signal.signal(signal.SIGTERM, stop_container)

# define chronicle message constants
CHRONICLE_MSGTYPE_FORK = 1001
CHRONICLE_MSGTYPE_BLOCK = 1002
CHRONICLE_MSGTYPE_TX_TRACE = 1003
CHRONICLE_MSGTYPE_ABI_UPD = 1004
CHRONICLE_MSGTYPE_ABI_REM = 1005
CHRONICLE_MSGTYPE_ABI_ERR = 1006
CHRONICLE_MSGTYPE_TBL_ROW = 1007
CHRONICLE_MSGTYPE_ENCODER_ERR = 1008
CHRONICLE_MSGTYPE_RCVR_PAUSE = 1009
CHRONICLE_MSGTYPE_BLOCK_COMPLETED = 1010

# basic message handler
async def handler(websocket, path):
	global action_buffer
	block_count = 0
	msgcount = 0
	tx_trace_count = 0
	start_time = datetime.utcnow()
	while KEEP_RUNNING:
		msg = await websocket.recv()
		msgtype = struct.unpack('i', msg[0:4])[0]
		value2 = struct.unpack('i', msg[4:8])[0]

		# todo - archive full message if option enabled
#		if ARCHIVE_MODE != 'OFF':
#			archive.addMessage(msg)

		if msgtype == CHRONICLE_MSGTYPE_FORK:
			msg = msg[8:].decode("utf-8", errors='ignore')
			msg = json.loads(msg)
			block_num = int(msg['block_num']) - 1
			logger.info(msg)
			logger.info('')
			await websocket.send(str(block_num))
			logger.info(f"Block {block_num} acknowledged (on fork)!")

		elif msgtype == CHRONICLE_MSGTYPE_BLOCK:
			block_count += 1
			if block_count % 100 == 0:
				block_count = 0
				msg = msg[8:].decode("utf-8", errors='ignore')
				msg = json.loads(msg)
#				logger.info(data)
				block_num = int(msg['block_num'])
				block = msg['block']
				block_timestamp = block['timestamp']

				# commit to ensure data written before block acknowledged
				if ARCHIVE_MODE != 'OFF':
					archive.commit(block_num, block_timestamp)

				await websocket.send(str(block_num))
				logger.info(f"Block {block_num} with timestamp {block_timestamp} acknowledged!")
#				logger.info(data)
#				logger.info('')

		elif msgtype == CHRONICLE_MSGTYPE_TX_TRACE:
			msg = msg[8:].decode("utf-8", errors='ignore')
			msg = json.loads(msg)
			block_num = int(msg['block_num'])
			block_timestamp = msg['block_timestamp']
			trace = msg['trace']
			tx_id = trace['id']
			cpu_usage_us = trace['cpu_usage_us']
			net_usage_words = trace['net_usage_words']
			action_traces = trace['action_traces']
			for action_trace in action_traces:
				receiver = action_trace['receiver']
				act = action_trace['act']
				account = act['account']
				name = act['name']
				auth = act['authorization']
				data = act['data']
				account_ram_deltas = action_trace['account_ram_deltas']
#				logger.info(f'{receiver} - {account} - {name} - {data}')


start_server = websockets.serve(handler, '0.0.0.0', 8800)
logger.info('Started Chronicle Consumer')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
