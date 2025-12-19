"""
Recursive file traversal for OmegaParser.

Walks directory structures and yields files for processing.
"""

from pathlib import Path
from typing import Iterator
import logging


logger = logging.getLogger("omegaparser")


class FileWalker:
    """
    Recursively walks directories and yields files for processing.
    """
    
    def __init__(self, root_path: Path):
        """
        Initialize walker with root directory.
        
        Args:
            root_path: Root directory to walk
        """
        self.root_path = root_path
        
        # Files to skip (common non-data files)
        self.skip_patterns = {
            '.DS_Store',
            'Thumbs.db',
            '.gitignore',
            '.gitkeep',
        }
        
        # Directories to skip
        self.skip_dirs = {
            '.git',
            '__pycache__',
            'node_modules',
            '.venv',
        }
    
    def walk(self) -> Iterator[Path]:
        """
        Recursively walk the directory tree and yield file paths.
        
        Yields:
            Path objects for each file found
        """
        if not self.root_path.exists():
            logger.error(f"Root path does not exist: {self.root_path}")
            return
        
        if not self.root_path.is_dir():
            logger.error(f"Root path is not a directory: {self.root_path}")
            return
        
        logger.info(f"Walking directory tree: {self.root_path}")
        file_count = 0
        
        for item in self._recursive_walk(self.root_path):
            file_count += 1
            if file_count % 100 == 0:
                logger.debug(f"Processed {file_count} files...")
            yield item
        
        logger.info(f"Found {file_count} total files")
    
    def _recursive_walk(self, current_path: Path) -> Iterator[Path]:
        """
        Internal recursive walker.
        """
        try:
            items = sorted(current_path.iterdir())
        except PermissionError:
            logger.warning(f"Permission denied: {current_path}")
            return
        except Exception as e:
            logger.warning(f"Error reading directory {current_path}: {e}")
            return
        
        for item in items:
            # Skip hidden files/directories (starting with .)
            if item.name.startswith('.') and item.name not in {'.json', '.csv'}:
                continue
            
            # Skip specific patterns
            if item.name in self.skip_patterns:
                continue
            
            if item.is_file():
                yield item
            elif item.is_dir():
                # Skip specific directories
                if item.name in self.skip_dirs:
                    continue
                
                # Recurse into subdirectories
                yield from self._recursive_walk(item)
            # Ignore symlinks and other special files
