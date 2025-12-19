"""
File type and content detection for OmegaParser.

Classifies files by type and attempts to detect the kind of content they contain.
"""

from pathlib import Path
from typing import Optional
import logging
import json

from .schemas import FileClassification
from .utils import safe_json_load, get_file_extension


logger = logging.getLogger("omegaparser")


class FileDetector:
    """
    Detects file types and classifies content.
    
    Uses soft classification - never fails, always provides a classification
    even if it's "unknown".
    """
    
    def detect(self, file_path: Path) -> FileClassification:
        """
        Detect file type and classify content.
        
        Args:
            file_path: Path to the file to classify
            
        Returns:
            FileClassification with type, content hint, and confidence
        """
        notes = []
        
        # Determine file type by extension and content
        file_type = self._detect_file_type(file_path, notes)
        
        # Attempt to classify content based on file type and structure
        content_likely, confidence = self._classify_content(
            file_path, file_type, notes
        )
        
        return FileClassification(
            file_path=str(file_path),
            file_type=file_type,
            content_likely=content_likely,
            confidence=confidence,
            notes=notes
        )
    
    def _detect_file_type(self, file_path: Path, notes: list) -> str:
        """
        Detect the file type based on extension and content.
        """
        ext = get_file_extension(file_path)
        
        # Map extensions to file types
        type_map = {
            'json': 'json',
            'csv': 'csv',
            'html': 'html',
            'htm': 'html',
            'txt': 'txt',
        }
        
        detected = type_map.get(ext, 'unknown')
        
        if detected == 'unknown' and ext:
            notes.append(f"Unknown extension: .{ext}")
        
        return detected
    
    def _classify_content(
        self, 
        file_path: Path, 
        file_type: str,
        notes: list
    ) -> tuple[str, str]:
        """
        Classify the likely content of the file.
        
        Returns:
            tuple: (content_type, confidence)
        """
        # Try to infer from filename
        filename_lower = file_path.name.lower()
        
        # YouTube/Google Takeout patterns
        if 'watch' in filename_lower or 'history' in filename_lower:
            if 'music' in filename_lower:
                return 'music-history', 'medium'
            return 'watch-history', 'medium'
        
        if 'comment' in filename_lower:
            return 'comments', 'medium'
        
        if 'search' in filename_lower:
            return 'search-history', 'medium'
        
        if 'subscription' in filename_lower:
            return 'subscriptions', 'medium'
        
        if 'playlist' in filename_lower:
            return 'playlists', 'medium'
        
        # For JSON files, try to peek at structure
        if file_type == 'json':
            data = safe_json_load(file_path)
            if data:
                return self._classify_json_structure(data, notes)
        
        # Default: unknown with low confidence
        notes.append("Could not determine content type from filename or structure")
        return 'unknown', 'low'
    
    def _classify_json_structure(self, data: any, notes: list) -> tuple[str, str]:
        """
        Attempt to classify JSON content by examining its structure.
        """
        # Handle array of records
        if isinstance(data, list):
            if len(data) == 0:
                notes.append("Empty JSON array")
                return 'empty', 'high'
            
            # Examine first record
            sample = data[0]
            if isinstance(sample, dict):
                return self._classify_dict_keys(sample, notes)
        
        # Handle single object
        elif isinstance(data, dict):
            return self._classify_dict_keys(data, notes)
        
        notes.append("Unexpected JSON structure")
        return 'unknown', 'low'
    
    def _classify_dict_keys(self, obj: dict, notes: list) -> tuple[str, str]:
        """
        Classify based on dictionary keys.
        """
        keys = set(obj.keys())
        
        # Common YouTube/Google Takeout patterns
        if 'title' in keys and 'titleUrl' in keys:
            return 'watch-event', 'high'
        
        if 'header' in keys and 'title' in keys:
            if 'products' in obj.get('header', ''):
                return 'watch-event', 'medium'
        
        if 'time' in keys and 'title' in keys:
            return 'media-event', 'medium'
        
        # Generic patterns
        if 'timestamp' in keys or 'time' in keys or 'date' in keys:
            return 'timestamped-event', 'low'
        
        notes.append(f"Unrecognized JSON structure with keys: {sorted(list(keys)[:5])}")
        return 'unknown', 'low'
