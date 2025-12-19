"""
OmegaParser - The last parser you'll ever need.

A first-pass ingestion and normalization parser for raw data exports.
"""

from .main import OmegaParser
from .schemas import NormalizedRecord, ProcessingSummary

__version__ = "0.1.0"
__all__ = ["OmegaParser", "NormalizedRecord", "ProcessingSummary"]
