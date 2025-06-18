import os
import asyncio
import tempfile
import aiofiles

class AsyncTempfile:
    def __init__(self):

        self._temp_file_path: str | None = None
        self._fd: int | None = None 
        
    async def create(self, prefix: str = 'subprober_file_') -> str:
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            await self.close()
        try:
            self._fd, self._temp_file_path = await asyncio.to_thread(
                tempfile.mkstemp,
                prefix=prefix,
                dir=tempfile.gettempdir()
            )
            await asyncio.to_thread(os.close, self._fd)
            self._fd = None 
            return self._temp_file_path
        
        except Exception as e:
            self._temp_file_path = None
            if self._fd is not None:
                try:
                    await asyncio.to_thread(os.close, self._fd)
                except OSError:
                    pass 
                finally:
                    self._fd = None
            raise 

    async def write(self, content: str) -> None:
        if not self._temp_file_path:
            raise IOError("Temporary file has not been created. Call create() first.")
        
        try:
            async with aiofiles.open(self._temp_file_path, "a") as f:
                await f.write(content)
        except Exception as e:
            raise

    async def read(self) -> str:
        if not self._temp_file_path or not os.path.exists(self._temp_file_path):
            raise IOError("Temporary file does not exist or has not been created.")

        try:
            async with aiofiles.open(self._temp_file_path, "r") as f:
                return await f.read()
        except Exception as e:
            raise

    async def readlines(self) -> list[str]:
        if not self._temp_file_path or not os.path.exists(self._temp_file_path):
            raise IOError("Temporary file does not exist or has not been created.")
        try:
            async with aiofiles.open(self._temp_file_path, "r") as f:
                return await f.readlines()
        except Exception as e:
            raise

    async def close(self) -> None:
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                await asyncio.to_thread(os.remove, self._temp_file_path)
            except Exception:
                pass
            finally:
                self._temp_file_path = None
                self._fd = None 
        else:
            self._temp_file_path = None 
            self._fd = None


    async def __aenter__(self):
        await self.create()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

