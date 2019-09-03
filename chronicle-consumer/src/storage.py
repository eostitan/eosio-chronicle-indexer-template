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
		pass

	def addMessage(self, msg):
		pass
