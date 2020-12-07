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
from pathlib import Path
from typing import Optional

from fedvision.framework.abc.executor import Executor
from fedvision.framework.utils.logger import Logger


class ProcessExecutor(Executor, Logger):
    def __init__(self, work_dir: Path):
        super().__init__(work_dir)

    async def execute(self, cmd) -> Optional[int]:
        self.info(f"execute cmd {cmd} at {self.working_dir}")
        try:
            sub = await asyncio.subprocess.create_subprocess_shell(
                cmd, shell=True, cwd=self.working_dir
            )
            await sub.communicate()
            return sub.returncode
        except Exception as e:
            self.error(e)
