# Copyright 2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

import shutil
import tempfile
from portage import os
from portage.tests import TestCase
from portage.const import PORTAGE_BIN_PATH
from portage.const import PORTAGE_PYM_PATH
from portage.const import BASH_BINARY
from _emerge.SpawnProcess import SpawnProcess
from _emerge.FifoIpcDaemon import FifoIpcDaemon
from _emerge.TaskScheduler import TaskScheduler

class IpcDaemonTestCase(TestCase):

	def testIpcDaemon(self):
		tmpdir = tempfile.mkdtemp()
		try:
			env = {}
			env['PORTAGE_BIN_PATH'] = PORTAGE_BIN_PATH
			env['PORTAGE_PYM_PATH'] = PORTAGE_PYM_PATH
			env['PORTAGE_BUILDDIR'] = tmpdir
			input_fifo = os.path.join(tmpdir, '.ipc_in')
			output_fifo = os.path.join(tmpdir, '.ipc_out')
			os.mkfifo(input_fifo)
			os.mkfifo(output_fifo)
			task_scheduler = TaskScheduler(max_jobs=2)
			daemon = FifoIpcDaemon(input_fifo=input_fifo,
				output_fifo=output_fifo,
				scheduler=task_scheduler.sched_iface)
			proc = SpawnProcess(
				args=[BASH_BINARY, "-c", '"$PORTAGE_BIN_PATH"/ebuild-ipc exit 0'],
				env=env, scheduler=task_scheduler.sched_iface)
			task_scheduler.add(daemon)
			task_scheduler.add(proc)
			task_scheduler.run()
			self.assertEqual(proc.returncode, os.EX_OK)
		finally:
			shutil.rmtree(tmpdir)
