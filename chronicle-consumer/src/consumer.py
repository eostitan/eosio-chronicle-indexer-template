import os
import asyncio
import websockets
import time
import signal
import json
import traceback
from datetime import datetime
from debug_log import logger

# if config to save all data
ARCHIVE_MODE = os.getenv('ARCHIVE_MODE', 'Off')
if ARCHIVE_MODE != 'Off':
	from storage import ArchiveStorage
	archive = ArchiveStorage()

# for gracefully handling docker signals
KEEP_RUNNING = True
def stop_container():
    global KEEP_RUNNING
    KEEP_RUNNING = False
signal.signal(signal.SIGTERM, stop_container)

# basic message handler
async def handler(websocket, path):
	global action_buffer
	block_count = 0
	while KEEP_RUNNING:
		msg = await websocket.recv()
		msg = msg.decode("utf-8", errors='ignore')

		# archive full message if option enabled
		if ARCHIVE_MODE != 'Off':
			archive.addMessage(msg)

		if msg[:18] == '{"msgtype":"BLOCK"':
			block_count += 1
			if block_count % 2500 == 0:
				block_count = 0
				j = json.loads(msg)
				data = j['data']
				block_num = int(data['block_num'])

				# commit to ensure data written before block acknowledged
				if ARCHIVE_MODE != 'Off':
					archive.commit(block_num)

				await websocket.send(str(block_num))
				logger.info(f"Block {block_num} acknowledged!")
#				logger.info(j)
#				logger.info('')

		elif msg[:21] == '{"msgtype":"TX_TRACE"':
			j = json.loads(msg)
			data = j['data']
			block_num = int(data['block_num'])
			trace = data['trace']
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
#				logger.info(f'{receiver} - {account} - {name} - {data}')

		elif msg[:20] == '{"msgtype":"TBL_ROW"':
			j = json.loads(msg)

		elif msg[:20] == '{"msgtype":"ABI_UPD"':
			j = json.loads(msg)

		elif msg[:24] == '{"msgtype":"ENCODER_ERR"':
			j = json.loads(msg)

		elif msg[:28] == '{"msgtype":"BLOCK_COMPLETED"':
			j = json.loads(msg)

		elif msg[:17] == '{"msgtype":"FORK"':
			j = json.loads(msg)

		else:
			j = json.loads(msg)
			logger.info(j)
			logger.info('')


start_server = websockets.serve(handler, '0.0.0.0', 8800)
logger.info('Started Chronicle Consumer')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
