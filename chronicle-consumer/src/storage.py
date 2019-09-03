import os
import asyncio
import time
import signal
import json
import traceback
from datetime import datetime
from debug_log import logger

ARCHIVE_MODE = os.getenv('ARCHIVE_MODE', '')
ARCHIVE_BLOCKS_PER_FILE = int(os.getenv('ARCHIVE_BLOCKS_PER_FILE', '100'))

class ArchiveStorage():
	def __init__(self, mode=ARCHIVE_MODE, block_per_file=ARCHIVE_BLOCKS_PER_FILE):
		try:
			os.mkdir('data-archive')
		except: pass
		self.messages = []

	def addMessage(self, msg):
		self.messages.append(msg)

	def commit(self, block_num):
		with open(f'data-archive/data-{block_num}.msg', 'w') as f:
			for msg in self.messages:
				f.write(msg)
		logger.info(f'Committed {len(self.messages)} messages')
		self.messages = []
