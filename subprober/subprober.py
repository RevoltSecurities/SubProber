from subprober.cli.cli import CLI
from subprober import Settings,PyRunner
from revoltlogger import Logger
from revoltutils import Banner
from gitupdater import GitUpdater
import asyncio

class Subprober:
    def __init__(self) -> None:
        self.cli = CLI().cli()
        self.settings = Settings(self.cli)
        self.logger = Logger(colored=not self.settings.no_color)
        self.bannerutils = Banner("subprober")
        self.gitutils = GitUpdater("RevoltSecurities/Subprober", "v3.1.0", "subprober")

    async def run(self) -> None:
        if self.settings.help:
            self.bannerutils.render()
            self.cli.display_help()
            exit(0)

        if not self.settings.silent:
            self.bannerutils.render()
            await self.gitutils.versionlog()

        if self.settings.update:
            updated = await self.gitutils.update()
            if updated:
                self.logger.info(f"Subprober updated to the latest version successfully")
                await self.gitutils.show_update_log()
                exit(0)
            else:
                self.logger.custom("failed", "Subprober updated failed, please update manually", "CRITICAL")
                exit(1)

        runner = PyRunner(self.settings)
        await runner.sprint()

def main():
    asyncio.run(Subprober().run())