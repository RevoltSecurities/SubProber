import os
import shutil
import asyncio
import tempfile

class AsyncTempdir:
    def __init__(self):
        self._temp_dir_path: str | None = None

    async def create(self) -> str:
        
        if self._temp_dir_path:
            await self.close()

        try:
            self._temp_dir_path = await asyncio.to_thread(
                tempfile.mkdtemp,
                prefix='subprober_',
                dir=tempfile.gettempdir()
            )
            return self._temp_dir_path
        except Exception as e:
            self._temp_dir_path = None 
            
    async def close(self) -> None:
        if self._temp_dir_path and os.path.exists(self._temp_dir_path):
            try:
                await asyncio.to_thread(shutil.rmtree, self._temp_dir_path)
            except Exception as e:
                pass
            finally:
                self._temp_dir_path = None

    async def __aenter__(self):
        return await self.create()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

