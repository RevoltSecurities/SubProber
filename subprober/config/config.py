from pathlib import Path
from appdirs import user_config_dir

class Config:
    def __init__(self, app_name: str = "Subprober"):
        self.app_name = app_name
        if not self.app_name:
            raise ValueError("App name is required")
        
    @property
    def config_dir(self) -> Path:
        return Path(user_config_dir(self.app_name))
    
    def config_provider(self) -> Path:
        return self.config_dir / "provider-config.yaml"