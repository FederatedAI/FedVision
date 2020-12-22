# Copyright (c) 2020 The FedVision Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
from pathlib import Path
from typing import Optional

from fedvision.framework.abc.executor import Executor
from fedvision.framework.utils.logger import Logger
from fedvision import FEDVISION_DATA_BASE_ENV


class ProcessExecutor(Executor, Logger):
    def __init__(self, work_dir: Path, data_dir=None):
        super().__init__(work_dir)
        self._data_dir = data_dir

    async def execute(self, cmd) -> Optional[int]:
        self.info(f"execute cmd {cmd} at {self.working_dir}")
        try:
            env = os.environ.copy()
            if self._data_dir is not None:
                env[FEDVISION_DATA_BASE_ENV] = self._data_dir
            sub = await asyncio.subprocess.create_subprocess_shell(
                cmd, shell=True, cwd=self.working_dir, env=env
            )
            await sub.communicate()
            return sub.returncode
        except Exception as e:
            self.error(e)
