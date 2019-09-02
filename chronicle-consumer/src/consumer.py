import logging
import asyncio
import websockets
import time
import signal
import json
import traceback
from datetime import datetime

# for gracefully handling docker signals
KEEP_RUNNING = True
def stop_container():
    global KEEP_RUNNING
    KEEP_RUNNING = False
signal.signal(signal.SIGTERM, stop_container)

# logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('debug.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


valid_actions = [('eosio.token', 'transfer')]

action_buffer_max_size = 25000
action_buffer = []

def get_unique_actions(block_num, block_time, trace, unique_actions):
	try:
		if (trace['account'], trace['name']) in valid_actions:
			d = {'block_num': block_num, 'time': block_time, 'account': trace['account'], 'name': trace['name']}
			d.update(trace['data'])
			if d not in unique_actions:
				unique_actions.append(d)
			for inline_trace in trace['inline_traces']:
				unique_actions = get_unique_actions(block_num, block_time, inline_trace, unique_actions)
	except:
		logger.error(traceback.format_exc())
	return unique_actions

async def handler(websocket, path):
	global action_buffer
	bcount = 0
	while KEEP_RUNNING:
		msg = await websocket.recv()
		msg = msg.decode("utf-8", errors='ignore')
		if msg[:18] == '{"msgtype":"BLOCK"':
			bcount += 1
			if bcount % 500 == 0:
				bcount = 0
				j = json.loads(msg)
				data = j['data']
				block_num = int(data['block_num'])
				await websocket.send(str(block_num))
				logger.info(f"Block {block_num} acknowledged!")
		


start_server = websockets.serve(handler, '0.0.0.0', 8800)
logger.info('Started Chronicle Consumer')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
