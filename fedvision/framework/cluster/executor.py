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
