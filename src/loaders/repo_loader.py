import os
import shutil
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import git

@dataclass
class RepoConfig:
    url: str
    branch: str = "main"
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                'node_modules', '__pycache__', '.git',
                '*.pyc', '*.log', 'dist', 'build', 'venv',
                '.venv', 'env', '.env', 'coverage', '.pytest_cache'
            ]

class RepositoryLoader:
    """Handles repository cloning and file filtering"""
    
    def __init__(self, working_dir: str = "./workspace"):
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(exist_ok=True)
        self.exclude_patterns = []
        
    def clone_repository(self, config: RepoConfig) -> Path:
        """Clone GitHub repository"""
        repo_name = config.url.split('/')[-1].replace('.git', '')
        repo_path = self.working_dir / repo_name
        
        if repo_path.exists():
            print(f"Removing existing directory: {repo_path}")
            shutil.rmtree(repo_path)
            
        print(f"Cloning {config.url}...")
        try:
            repo = git.Repo.clone_from(
                config.url, 
                repo_path,
                branch=config.branch,
                depth=1  # Shallow clone for efficiency
            )
            print(f"Successfully cloned to {repo_path}")
            return repo_path
        except Exception as e:
            print(f"Error cloning repository: {e}")
            raise
    
    def get_source_files(self, repo_path: Path, extensions: List[str]) -> List[Path]:
        """Get all source files with given extensions"""
        source_files = []
        
        for ext in extensions:
            for file_path in repo_path.rglob(f"*{ext}"):
                if self._should_include(file_path, repo_path):
                    source_files.append(file_path)
                    
        print(f"Found {len(source_files)} source files with extensions {extensions}")
        return source_files
    
    def _should_include(self, file_path: Path, repo_path: Path) -> bool:
        """Check if file should be included based on patterns"""
        try:
            rel_path = str(file_path.relative_to(repo_path))
        except ValueError:
            return False
            
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in rel_path:
                return False
                
        # Skip very large files (over 1MB)
        if file_path.stat().st_size > 1024 * 1024:
            return False
            
        return True