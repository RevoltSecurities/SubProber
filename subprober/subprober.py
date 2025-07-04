import asyncio
from subprober.cli.cli import CLI
from subprober.banner.banner import Banner
from subprober.config.config import Config
from subprober.gitutils.gitutils import GitUtils
from subprober.logger.logger import Logger
from subprober.help.help import Help
from subprober.version.version import Version
from subprober.pyrunner.pyrunner import Runner
from subprober.validate.validate import check_browsers, install_browsers
import tempfile
import sys

class Subprober:
    def __init__(self):
        self.cli = CLI()
        self.args = self.cli.cli()
        self.config = Config()
        self.tmpdir = tempfile.gettempdir()
        self.git = GitUtils("RevoltSecurities/Subprober", "subprober", self.tmpdir)
        self.version = Version()
        self.gitversion = self.version.gitversion
        self.pypi_version = self.version.pypi
        self.help = Help()
        self.banner = Banner("Subprober")
        self.logger = Logger()
        self.runner = Runner(self.args)
        
    async def Version(self) -> None:
        currentgit = await self.git.git_version()
        if not currentgit:
            self.logger.warn("unable to get the latest version of subprober")
            return
        
        if currentgit == self.gitversion:
                print(f"[{self.logger.blue}{self.logger.bold}version{self.logger.reset}]:{self.logger.bold}{self.logger.white}subprober current version {self.gitversion} ({self.logger.green}latest{self.logger.reset}{self.logger.bold}{self.logger.white}){self.logger.reset}", file=sys.stderr)
        else:
                print(f"[{self.logger.blue}{self.logger.bold}version{self.logger.reset}]:{self.logger.bold}{self.logger.white}subprober current version {self.gitversion} ({self.logger.red}outdated{self.logger.reset}{self.logger.bold}{self.logger.white}){self.logger.reset}", file=sys.stderr)
        return
    
    async def update(self,update,show_updates) -> None:
        if show_updates:
            await self.git.show_update_log()
            return
        
        if update:
            current = await self.git.git_version()
            if not current:
                self.logger.warn("unable to get the latest version of Subprober")
                return
                
            if current == self.gitversion:
                self.logger.info("Subprober is already in latest version")
                return
                
            zipurl = await self.git.fetch_latest_zip_url()
            if not zipurl:
                self.logger.warn("unable to get the latest source code of Subprober")
                return
                
            await self.git.download_and_install(zipurl)
            newpypi = self.git.current_version()
            if newpypi == self.pypi_version:
                self.logger.warn("unable to update Subprober to the latest version, please try manually")
                return
                
            self.logger.info(f"Subprober has been updated to latest version")
            await self.git.show_update_log()
            return
        
    async def run(self) -> None:
        try:
            if self.args.help:
                self.banner.render()
                self.help.display_help()
                return
            
            if not self.args.silent:
                self.banner.render()
                await self.Version()
            
            if self.args.update or self.args.show_updates:
                await self.update(self.args.update, self.args.show_updates)
                exit(0)
            
            if self.args.screenshot:
                browser = await check_browsers(self.args.verbose)
                if browser:
                    if self.args.verbose:
                        self.logger.info(f"Browsers are already installed!")
                if not browser:
                    self.logger.info(f"Installing Browsers for Headless modes")
                    await install_browsers(self.args.verbose)
            
            await self.runner.sprint()
        except Exception as e:
            self.logger.warn(f"Error occurred in the run method of subprober due to: {e}")
            exit()
            

def main():
    prober = Subprober()
    asyncio.run(prober.run())
    
if __name__ == "__main__":
    main()