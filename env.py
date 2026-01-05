import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this file is located (project root)
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    # Also try loading from current directory (in case .env is in cwd)
    load_dotenv()


def env(key, default=None, warn_default=True):
    """
    Get environment variable value with optional warning for defaults.

    Args:
        key (str): Environment variable name
        default: Default value if not found
        warn_default (bool): Print warning if using default value

    Returns:
        Environment variable value or default
    """
    value = os.getenv(key)

    if value is None and default is not None and warn_default:
        print(
            f"⚠️  WARNING: Using default value for '{key}': '{default}' - Consider setting it in .env file"
        )

    return value if value is not None else default
