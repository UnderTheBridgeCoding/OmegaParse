"""
ZIP and directory ingestion for OmegaParser.

Handles extraction of ZIP files and preparation of input directories.
"""

import tempfile
import zipfile
from pathlib import Path
from typing import Optional
import logging
import shutil


logger = logging.getLogger("omegaparser")


class Ingester:
    """
    Handles ingestion of input data (ZIP files or directories).
    """
    
    def __init__(self):
        self.temp_dir: Optional[Path] = None
        self.workspace: Optional[Path] = None
    
    def ingest(self, input_path: str) -> Path:
        """
        Ingest input (ZIP or directory) and return path to workspace.
        
        Args:
            input_path: Path to ZIP file or directory
            
        Returns:
            Path to the workspace directory containing the data
        """
        path = Path(input_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")
        
        if path.is_file() and path.suffix.lower() == '.zip':
            return self._extract_zip(path)
        elif path.is_dir():
            return self._use_directory(path)
        else:
            raise ValueError(
                f"Input must be a ZIP file or directory, got: {input_path}"
            )
    
    def _extract_zip(self, zip_path: Path) -> Path:
        """
        Extract ZIP file to a temporary workspace.
        """
        logger.info(f"Extracting ZIP file: {zip_path}")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="omegaparser_"))
        self.workspace = self.temp_dir / "extracted"
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.workspace)
            
            logger.info(f"Extracted to: {self.workspace}")
            return self.workspace
            
        except zipfile.BadZipFile as e:
            self.cleanup()
            raise ValueError(f"Invalid ZIP file: {e}")
        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to extract ZIP: {e}")
    
    def _use_directory(self, dir_path: Path) -> Path:
        """
        Use an existing directory as the workspace.
        """
        logger.info(f"Using directory: {dir_path}")
        self.workspace = dir_path
        return self.workspace
    
    def cleanup(self) -> None:
        """
        Clean up temporary files and directories.
        """
        if self.temp_dir and self.temp_dir.exists():
            logger.debug(f"Cleaning up temporary directory: {self.temp_dir}")
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp dir: {e}")
            finally:
                self.temp_dir = None
                self.workspace = None
