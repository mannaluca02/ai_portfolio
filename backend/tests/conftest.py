"""Offline tests: never read .env, connect to production, or download a model."""
import importlib
import os
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["OPENAI_API_KEY"] = "offline-test-key"
os.environ["SKIP_VERIFICATION"] = "false"

from pydantic_settings import BaseSettings

original_init = BaseSettings.__init__


def offline_settings(self, **kwargs):
    original_init(self, _env_file=None, **kwargs)


with patch.object(BaseSettings, "__init__", offline_settings):
    importlib.import_module("app.config")

# The neural model is an external dependency, replaced only in this offline suite.
stub = ModuleType("sentence_transformers")


class OfflineModel:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("Inject a mock embedding service in offline tests")


stub.SentenceTransformer = OfflineModel
sys.modules["sentence_transformers"] = stub
