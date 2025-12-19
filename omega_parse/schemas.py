"""
Intermediate data models for OmegaParser.

These schemas define the normalized structure that all input data
is transformed into, preserving both raw and normalized forms.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from datetime import datetime


@dataclass
class NormalizedRecord:
    """
    Common intermediate structure for all parsed content.
    
    Preserves original raw data alongside normalized fields.
    """
    # Identity
    record_id: str
    source_file: str
    
    # Classification (soft, non-destructive)
    content_type: str  # video, music-video, watch-event, comment, search, unknown
    source_type: str   # channel, platform-surface, unknown
    
    # Normalized fields (None means field not present or uncertain)
    title: Optional[str] = None
    timestamp: Optional[datetime] = None
    timestamp_uncertain: bool = False
    channel: Optional[str] = None
    url: Optional[str] = None
    
    # Preservation of original data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata about the parsing process
    detected_format: Optional[str] = None  # json, csv, html, txt, unknown
    parsing_notes: List[str] = field(default_factory=list)


@dataclass
class FileClassification:
    """
    Result of file type detection and content classification.
    """
    file_path: str
    file_type: str  # json, csv, html, txt, unknown
    content_likely: str  # What kind of content this appears to contain
    confidence: str  # high, medium, low
    notes: List[str] = field(default_factory=list)


@dataclass
class ProcessingSummary:
    """
    High-level summary of the parsing process.
    """
    total_files: int = 0
    total_records: int = 0
    
    # Counts by content type
    by_content_type: Dict[str, int] = field(default_factory=dict)
    
    # Counts by source
    by_source: Dict[str, int] = field(default_factory=dict)
    
    # Counts by file type
    by_file_type: Dict[str, int] = field(default_factory=dict)
    
    # Files that couldn't be classified
    unclassified_files: List[str] = field(default_factory=list)
    
    # Records with uncertain classification
    uncertain_records: int = 0
    
    # Processing metadata
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    input_path: Optional[str] = None
    output_path: Optional[str] = None
