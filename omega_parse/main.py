"""
Main orchestration for OmegaParser.

Coordinates the ingestion, detection, normalization, aggregation, and emission pipeline.
"""

from pathlib import Path
from datetime import datetime
import logging

from .ingest import Ingester
from .walkers import FileWalker
from .detectors import FileDetector
from .normalizers import Normalizer
from .aggregators import Aggregator
from .emitters import Emitter
from .schemas import ProcessingSummary
from .utils import setup_logging


logger = logging.getLogger("omegaparser")


class OmegaParser:
    """
    Main parser orchestrator.
    
    Coordinates the full pipeline:
    1. Ingest (ZIP or directory)
    2. Walk files
    3. Detect & classify
    4. Normalize to common schema
    5. Aggregate counts
    6. Emit JSON outputs
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize OmegaParser.
        
        Args:
            verbose: Enable verbose logging
        """
        level = logging.DEBUG if verbose else logging.INFO
        setup_logging(level)
        
        self.ingester = Ingester()
        self.detector = FileDetector()
        self.normalizer = Normalizer()
    
    def parse(self, input_path: str, output_path: str) -> ProcessingSummary:
        """
        Parse input data and write structured outputs.
        
        Args:
            input_path: Path to ZIP file or directory
            output_path: Path to output directory
            
        Returns:
            ProcessingSummary with statistics about the processing
        """
        logger.info("=" * 60)
        logger.info("OmegaParser - The last parser you'll ever need")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Ingest
            logger.info(f"Ingesting: {input_path}")
            workspace = self.ingester.ingest(input_path)
            
            # Step 2: Walk files
            logger.info("Walking directory tree...")
            walker = FileWalker(workspace)
            
            # Step 3: Initialize aggregation
            aggregator = Aggregator()
            aggregator.summary.start_time = start_time
            aggregator.summary.input_path = input_path
            aggregator.summary.output_path = output_path
            
            # Step 4: Process each file
            logger.info("Processing files...")
            for file_path in walker.walk():
                # Detect file type and content
                classification = self.detector.detect(file_path)
                aggregator.add_file(classification)
                
                # Normalize to common schema
                records = self.normalizer.normalize_file(file_path, classification)
                
                # Aggregate
                aggregator.add_records(records)
            
            # Step 5: Finalize summary
            end_time = datetime.now()
            aggregator.summary.end_time = end_time
            summary = aggregator.get_summary()
            
            # Step 6: Emit outputs
            logger.info(f"Writing outputs to: {output_path}")
            emitter = Emitter(Path(output_path))
            
            emitter.emit_summary(summary)
            emitter.emit_by_content_type(aggregator.get_records_by_content_type())
            emitter.emit_by_channel(aggregator.get_records_by_channel())
            emitter.emit_unclassified(aggregator.get_unclassified_records())
            
            # Log summary
            duration = (end_time - start_time).total_seconds()
            logger.info("=" * 60)
            logger.info("Processing complete!")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Files processed: {summary.total_files}")
            logger.info(f"Records extracted: {summary.total_records}")
            logger.info(f"Unclassified files: {len(summary.unclassified_files)}")
            logger.info(f"Uncertain records: {summary.uncertain_records}")
            logger.info("=" * 60)
            
            return summary
            
        finally:
            # Clean up temporary files
            self.ingester.cleanup()
