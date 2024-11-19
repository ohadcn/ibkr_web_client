from dataclasses import dataclass
from pathlib import Path
import sys

from .ibkr_types.enums import IBKRRealms


@dataclass
class IBKRConfig:
    token_access: str
    token_secret: str
    consumer_key: str
    dh_param_path: Path
    dh_private_encryption_path: Path
    dh_private_signature_path: Path
    update_session_interval: int = 60 * 5  # 5 minutes

    def __post_init__(self):
        # Validation of the configs
        if self.token_access is None or len(self.token_access) == 0:
            raise ValueError("Token access is required")
        if self.token_secret is None or len(self.token_secret) == 0:
            raise ValueError("Token secret is required")
        if self.consumer_key is None or len(self.consumer_key) == 0:
            raise ValueError("Consumer key is required")
        if self.dh_param_path is None or not self.dh_param_path.exists():
            raise ValueError("DH param path is required and must point to existing file")
        if self.dh_private_encryption_path is None or not self.dh_private_encryption_path.exists():
            raise ValueError("DH private encryption path is required and must point to existing file")
        if self.dh_private_signature_path is None or not self.dh_private_signature_path.exists():
            raise ValueError("DH private signature path is required and must point to existing file")

    @property
    def realm(self) -> str:
        return IBKRRealms.TEST.value if self.consumer_key == "TESTCONS" else IBKRRealms.LIMITED_POA.value

    @property
    def python_version(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    @property
    def base_url(self) -> str:
        return "https://api.ibkr.com/v1/api"
