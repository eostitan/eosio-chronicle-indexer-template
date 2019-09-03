import os
import asyncio
import time
import signal
import json
import traceback
from datetime import datetime
from debug_log import logger

ARCHIVE_MODE = os.getenv('ARCHIVE_MODE', 'OFF')

class ArchiveStorage():
	def __init__(self, mode=ARCHIVE_MODE):
		try:
			os.mkdir('data-archive')
		except: pass
		self.messages = []

	def addMessage(self, msg):
		self.messages.append(msg)

	def commit(self, block_num, block_timestamp):
		with open(f'data-archive/data-{block_num}.msg', 'w') as f:
			for msg in self.messages:
				f.write(msg)
		logger.info(f'ARCHIVE - Committed {len(self.messages)} messages to time {block_timestamp}')
		self.messages = []
