"""
Data aggregation and counting for OmegaParser.

Produces counts and summaries from normalized records.
"""

from typing import List, Dict
from collections import defaultdict
import logging

from .schemas import NormalizedRecord, ProcessingSummary, FileClassification


logger = logging.getLogger("omegaparser")


class Aggregator:
    """
    Aggregates normalized records into counts and summaries.
    """
    
    def __init__(self):
        self.summary = ProcessingSummary()
        self.records_by_content_type: Dict[str, List[NormalizedRecord]] = defaultdict(list)
        self.records_by_channel: Dict[str, List[NormalizedRecord]] = defaultdict(list)
        self.unclassified_records: List[NormalizedRecord] = []
    
    def add_records(self, records: List[NormalizedRecord]) -> None:
        """
        Add records to the aggregator for counting and grouping.
        
        Args:
            records: List of NormalizedRecord objects to aggregate
        """
        for record in records:
            self.summary.total_records += 1
            
            # Count by content type
            content_type = record.content_type
            self.summary.by_content_type[content_type] = \
                self.summary.by_content_type.get(content_type, 0) + 1
            self.records_by_content_type[content_type].append(record)
            
            # Count by source/channel
            if record.channel:
                channel = record.channel
                self.summary.by_source[channel] = \
                    self.summary.by_source.get(channel, 0) + 1
                self.records_by_channel[channel].append(record)
            else:
                source_type = record.source_type
                self.summary.by_source[source_type] = \
                    self.summary.by_source.get(source_type, 0) + 1
            
            # Track unclassified
            if content_type == 'unknown' or record.source_type == 'unknown':
                self.unclassified_records.append(record)
            
            # Track uncertainty
            if record.timestamp_uncertain or len(record.parsing_notes) > 0:
                self.summary.uncertain_records += 1
            
            # Count by file type
            if record.detected_format:
                fmt = record.detected_format
                self.summary.by_file_type[fmt] = \
                    self.summary.by_file_type.get(fmt, 0) + 1
    
    def add_file(self, classification: FileClassification) -> None:
        """
        Track file-level statistics.
        
        Args:
            classification: FileClassification for the processed file
        """
        self.summary.total_files += 1
        
        if classification.confidence == 'low' or classification.content_likely == 'unknown':
            self.summary.unclassified_files.append(classification.file_path)
    
    def get_summary(self) -> ProcessingSummary:
        """
        Get the current processing summary.
        
        Returns:
            ProcessingSummary object with current counts
        """
        return self.summary
    
    def get_records_by_content_type(self) -> Dict[str, List[NormalizedRecord]]:
        """
        Get all records grouped by content type.
        
        Returns:
            Dictionary mapping content type to list of records
        """
        return dict(self.records_by_content_type)
    
    def get_records_by_channel(self) -> Dict[str, List[NormalizedRecord]]:
        """
        Get all records grouped by channel/source.
        
        Returns:
            Dictionary mapping channel/source to list of records
        """
        return dict(self.records_by_channel)
    
    def get_unclassified_records(self) -> List[NormalizedRecord]:
        """
        Get all records that could not be fully classified.
        
        Returns:
            List of unclassified NormalizedRecord objects
        """
        return self.unclassified_records
