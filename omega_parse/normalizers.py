"""
Schema normalization for OmegaParser.

Converts disparate file formats and structures into the common
intermediate representation defined in schemas.py.
"""

from pathlib import Path
from typing import List, Optional, Any, Dict
import logging
import json
import csv

from .schemas import NormalizedRecord, FileClassification
from .utils import generate_record_id, safe_json_load, parse_timestamp, MAX_RAW_CONTENT_LENGTH


logger = logging.getLogger("omegaparser")


class Normalizer:
    """
    Normalizes various file formats into the common intermediate schema.
    """
    
    def normalize_file(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Normalize a file into a list of NormalizedRecord objects.
        
        Args:
            file_path: Path to the file
            classification: File classification from detector
            
        Returns:
            List of NormalizedRecord objects
        """
        file_type = classification.file_type
        
        try:
            if file_type == 'json':
                return self._normalize_json(file_path, classification)
            elif file_type == 'csv':
                return self._normalize_csv(file_path, classification)
            elif file_type == 'html':
                return self._normalize_html(file_path, classification)
            elif file_type == 'txt':
                return self._normalize_txt(file_path, classification)
            else:
                return self._normalize_unknown(file_path, classification)
        except Exception as e:
            logger.warning(f"Error normalizing {file_path}: {e}")
            return self._create_error_record(file_path, classification, str(e))
    
    def _normalize_json(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Normalize JSON file.
        """
        data = safe_json_load(file_path)
        
        if data is None:
            return self._create_error_record(
                file_path, classification, "Failed to parse JSON"
            )
        
        records = []
        
        # Handle array of records
        if isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    record = self._normalize_json_object(
                        item, file_path, idx, classification
                    )
                    records.append(record)
        
        # Handle single object
        elif isinstance(data, dict):
            record = self._normalize_json_object(
                data, file_path, 0, classification
            )
            records.append(record)
        
        return records
    
    def _normalize_json_object(
        self,
        obj: Dict[str, Any],
        file_path: Path,
        index: int,
        classification: FileClassification
    ) -> NormalizedRecord:
        """
        Normalize a single JSON object into a NormalizedRecord.
        """
        record_id = generate_record_id(str(file_path), index)
        
        # Extract common fields with various key patterns
        title = self._extract_field(obj, ['title', 'name', 'header'])
        
        # Extract timestamp
        timestamp_str = self._extract_field(
            obj, ['timestamp', 'time', 'date', 'created_at', 'createdAt']
        )
        timestamp, uncertain = parse_timestamp(timestamp_str) if timestamp_str else (None, True)
        
        # Extract channel/source
        channel = self._extract_field(
            obj, ['channel', 'channelName', 'subtitles', 'author']
        )
        
        # Extract URL
        url = self._extract_field(
            obj, ['url', 'titleUrl', 'link', 'href']
        )
        
        # Determine content type and source type
        content_type = self._infer_content_type(obj, classification)
        source_type = self._infer_source_type(obj, channel)
        
        notes = []
        if uncertain:
            notes.append("Timestamp could not be parsed or is missing")
        
        return NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type=content_type,
            source_type=source_type,
            title=title,
            timestamp=timestamp,
            timestamp_uncertain=uncertain,
            channel=channel,
            url=url,
            raw_data=obj,
            detected_format='json',
            parsing_notes=notes
        )
    
    def _normalize_csv(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Normalize CSV file.
        """
        records = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Try to detect dialect
                sample = f.read(4096)
                f.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = csv.excel
                
                reader = csv.DictReader(f, dialect=dialect)
                
                for idx, row in enumerate(reader):
                    record = self._normalize_csv_row(
                        row, file_path, idx, classification
                    )
                    records.append(record)
        
        except Exception as e:
            logger.warning(f"Error reading CSV {file_path}: {e}")
            return self._create_error_record(file_path, classification, str(e))
        
        return records
    
    def _normalize_csv_row(
        self,
        row: Dict[str, str],
        file_path: Path,
        index: int,
        classification: FileClassification
    ) -> NormalizedRecord:
        """
        Normalize a single CSV row into a NormalizedRecord.
        """
        record_id = generate_record_id(str(file_path), index)
        
        # Extract fields (CSV keys are case-sensitive)
        title = self._extract_field_case_insensitive(
            row, ['title', 'name', 'video title']
        )
        
        timestamp_str = self._extract_field_case_insensitive(
            row, ['timestamp', 'time', 'date']
        )
        timestamp, uncertain = parse_timestamp(timestamp_str) if timestamp_str else (None, True)
        
        channel = self._extract_field_case_insensitive(
            row, ['channel', 'channel name', 'artist']
        )
        
        url = self._extract_field_case_insensitive(
            row, ['url', 'link', 'video url']
        )
        
        content_type = self._infer_content_type(row, classification)
        source_type = self._infer_source_type(row, channel)
        
        notes = []
        if uncertain:
            notes.append("Timestamp could not be parsed or is missing")
        
        return NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type=content_type,
            source_type=source_type,
            title=title,
            timestamp=timestamp,
            timestamp_uncertain=uncertain,
            channel=channel,
            url=url,
            raw_data=dict(row),
            detected_format='csv',
            parsing_notes=notes
        )
    
    def _normalize_html(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Normalize HTML file (basic handling - just store as unknown).
        """
        record_id = generate_record_id(str(file_path), 0)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
        
        return [NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type='unknown',
            source_type='unknown',
            raw_data={'html_content': content[:MAX_RAW_CONTENT_LENGTH]},
            detected_format='html',
            parsing_notes=['HTML files are not fully parsed - stored as unknown']
        )]
    
    def _normalize_txt(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Normalize text file (basic handling - just store as unknown).
        """
        record_id = generate_record_id(str(file_path), 0)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
        
        return [NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type='unknown',
            source_type='unknown',
            raw_data={'text_content': content[:MAX_RAW_CONTENT_LENGTH]},
            detected_format='txt',
            parsing_notes=['Text files are not fully parsed - stored as unknown']
        )]
    
    def _normalize_unknown(
        self, 
        file_path: Path, 
        classification: FileClassification
    ) -> List[NormalizedRecord]:
        """
        Handle unknown file types.
        """
        record_id = generate_record_id(str(file_path), 0)
        
        return [NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type='unknown',
            source_type='unknown',
            raw_data={'file_type': classification.file_type},
            detected_format='unknown',
            parsing_notes=[f'Unknown file type: {classification.file_type}']
        )]
    
    def _create_error_record(
        self,
        file_path: Path,
        classification: FileClassification,
        error: str
    ) -> List[NormalizedRecord]:
        """
        Create an error record for files that failed to parse.
        """
        record_id = generate_record_id(str(file_path), 0)
        
        return [NormalizedRecord(
            record_id=record_id,
            source_file=str(file_path),
            content_type='unknown',
            source_type='unknown',
            raw_data={'error': error},
            detected_format=classification.file_type,
            parsing_notes=[f'Parsing error: {error}']
        )]
    
    def _extract_field(self, obj: Dict[str, Any], keys: List[str]) -> Optional[str]:
        """
        Extract a field from object trying multiple possible keys.
        Handles nested structures and lists.
        """
        for key in keys:
            if key in obj:
                value = obj[key]
                if value:
                    # Handle list of dicts (e.g., subtitles: [{"name": "Channel"}])
                    if isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], dict) and 'name' in value[0]:
                            return str(value[0]['name'])
                        # For simple lists, join them
                        return ', '.join(str(v) for v in value)
                    return str(value)
        return None
    
    def _extract_field_case_insensitive(
        self, 
        obj: Dict[str, str], 
        keys: List[str]
    ) -> Optional[str]:
        """
        Extract a field from object trying multiple keys (case-insensitive).
        """
        obj_lower = {k.lower(): v for k, v in obj.items()}
        
        for key in keys:
            if key.lower() in obj_lower:
                value = obj_lower[key.lower()]
                if value:
                    return str(value)
        return None
    
    def _infer_content_type(
        self, 
        obj: Dict[str, Any], 
        classification: FileClassification
    ) -> str:
        """
        Infer content type from object and classification.
        """
        # Use classification hint if available
        content_hint = classification.content_likely
        
        if content_hint in ['watch-history', 'watch-event']:
            return 'watch-event'
        elif content_hint in ['music-history']:
            return 'music-video'
        elif content_hint == 'comments':
            return 'comment'
        elif content_hint in ['search-history']:
            return 'search'
        elif content_hint in ['media-event', 'timestamped-event']:
            return 'video'
        
        # Default to unknown
        return 'unknown'
    
    def _infer_source_type(self, obj: Dict[str, Any], channel: Optional[str]) -> str:
        """
        Infer source type from object data.
        """
        if channel:
            return 'channel'
        
        # Check for platform indicators
        if isinstance(obj, dict):
            if 'products' in str(obj.get('header', '')).lower():
                return 'platform-surface'
        
        return 'unknown'
