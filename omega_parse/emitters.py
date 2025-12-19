"""
Output writers for OmegaParser.

Emits deterministic, inspectable JSON output files.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

from .schemas import NormalizedRecord, ProcessingSummary
from .utils import ensure_output_dir


logger = logging.getLogger("omegaparser")


class Emitter:
    """
    Writes output files in structured JSON format.
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize emitter with output directory.
        
        Args:
            output_dir: Directory where output files will be written
        """
        self.output_dir = output_dir
        ensure_output_dir(output_dir)
    
    def emit_summary(self, summary: ProcessingSummary) -> None:
        """
        Write summary.json with high-level processing statistics.
        
        Args:
            summary: ProcessingSummary object to write
        """
        output_path = self.output_dir / "summary.json"
        
        summary_dict = {
            "total_files": summary.total_files,
            "total_records": summary.total_records,
            "by_content_type": summary.by_content_type,
            "by_source": summary.by_source,
            "by_file_type": summary.by_file_type,
            "unclassified_files_count": len(summary.unclassified_files),
            "uncertain_records_count": summary.uncertain_records,
            "processing_metadata": {
                "start_time": summary.start_time.isoformat() if summary.start_time else None,
                "end_time": summary.end_time.isoformat() if summary.end_time else None,
                "input_path": summary.input_path,
                "output_path": summary.output_path,
            }
        }
        
        self._write_json(output_path, summary_dict)
        logger.info(f"Wrote summary to {output_path}")
    
    def emit_by_content_type(
        self, 
        records_by_type: Dict[str, List[NormalizedRecord]]
    ) -> None:
        """
        Write by_content_type.json with records grouped by content type.
        
        Args:
            records_by_type: Dictionary mapping content type to records
        """
        output_path = self.output_dir / "by_content_type.json"
        
        output = {}
        for content_type, records in records_by_type.items():
            output[content_type] = {
                "count": len(records),
                "records": [self._record_to_dict(r) for r in records]
            }
        
        self._write_json(output_path, output)
        logger.info(f"Wrote content type groups to {output_path}")
    
    def emit_by_channel(
        self, 
        records_by_channel: Dict[str, List[NormalizedRecord]]
    ) -> None:
        """
        Write by_channel.json with records grouped by channel/source.
        
        Args:
            records_by_channel: Dictionary mapping channel to records
        """
        output_path = self.output_dir / "by_channel.json"
        
        output = {}
        for channel, records in records_by_channel.items():
            output[channel] = {
                "count": len(records),
                "records": [self._record_to_dict(r) for r in records]
            }
        
        self._write_json(output_path, output)
        logger.info(f"Wrote channel groups to {output_path}")
    
    def emit_unclassified(
        self, 
        unclassified_records: List[NormalizedRecord]
    ) -> None:
        """
        Write unclassified.json with records that could not be fully classified.
        
        Args:
            unclassified_records: List of unclassified records
        """
        output_path = self.output_dir / "unclassified.json"
        
        output = {
            "count": len(unclassified_records),
            "records": [self._record_to_dict(r) for r in unclassified_records]
        }
        
        self._write_json(output_path, output)
        logger.info(f"Wrote unclassified records to {output_path}")
    
    def _record_to_dict(self, record: NormalizedRecord) -> Dict[str, Any]:
        """
        Convert a NormalizedRecord to a dictionary for JSON serialization.
        """
        return {
            "record_id": record.record_id,
            "source_file": record.source_file,
            "content_type": record.content_type,
            "source_type": record.source_type,
            "title": record.title,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            "timestamp_uncertain": record.timestamp_uncertain,
            "channel": record.channel,
            "url": record.url,
            "raw_data": record.raw_data,
            "detected_format": record.detected_format,
            "parsing_notes": record.parsing_notes,
        }
    
    def _write_json(self, path: Path, data: Any) -> None:
        """
        Write data to a JSON file with consistent formatting.
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
