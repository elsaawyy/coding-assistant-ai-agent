"""
Core Agent - Main orchestrator for the Coding Assistant AI Agent
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.loaders.repo_loader import RepositoryLoader, RepoConfig
from src.analyzers.code_analyzer import PythonAnalyzer
from src.detectors.issue_detector import IssueDetector, Severity
from src.agents.decision_engine import DecisionEngine, Action, ActionType, FixStrategy


@dataclass
class AgentState:
    current_file: str = ""
    files_processed: int = 0
    files_with_issues: int = 0
    total_issues_found: int = 0
    fixes_applied: int = 0
    fixes_failed: int = 0
    fixes_skipped: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time


class CodingAssistantAgent:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.repo_loader = RepositoryLoader(working_dir=config.get('workspace_dir', './workspace'))
        self.analyzer = PythonAnalyzer()
        self.detector = IssueDetector()
        self.decision_engine = DecisionEngine(config)
        self.state = AgentState()
        self.analysis_results = []
        self.all_issues = []
        self.applied_fixes = []
        self.dry_run = config.get('dry_run', False)
        
    async def run(self, repo_url: str) -> Dict[str, Any]:
        print("=" * 60)
        print("🤖 CODING ASSISTANT AI AGENT")
        print("=" * 60)
        print(f"Repository: {repo_url}")
        
        # Load repository
        repo_path = self.repo_loader.clone_repository(RepoConfig(url=repo_url))
        
        # Get source files
        source_files = self.repo_loader.get_source_files(repo_path, ['.py'])
        print(f"\n📁 Found {len(source_files)} source files\n")
        
        # Process each file
        for idx, file_path in enumerate(source_files, 1):
            await self._process_file(file_path, idx, len(source_files))
        
        # Generate report
        return self._generate_report()
    
    async def _process_file(self, file_path: Path, current: int, total: int):
        print(f"\n📄 [{current}/{total}] Analyzing: {file_path.name}")
        
        try:
            analysis = self.analyzer.analyze_file(file_path)
            if 'error' in analysis:
                print(f"⚠️ Skipping - Parse error")
                return
            
            self.analysis_results.append(analysis)
            issues = self.detector.detect_issues(analysis)
            self.all_issues.extend(issues)
            self.state.total_issues_found += len(issues)
            
            if not issues:
                print(f"✅ No issues found")
                return
            
            # Print summary
            severity_counts = {}
            for issue in issues:
                severity_counts[issue.severity.name] = severity_counts.get(issue.severity.name, 0) + 1
            
            print(f"🐛 Found {len(issues)} issues:")
            for sev, count in severity_counts.items():
                print(f"  • {sev}: {count}")
            
            # Get decisions
            actions = self.decision_engine.prioritize_issues(issues, str(file_path))
            
            # Process actions (no recording in dry run)
            for action in actions[:3]:  # Limit to 3 per file
                if action.type == ActionType.FIX:
                    if self.dry_run:
                        print(f"  🔍 [DRY RUN] Would fix: {action.issue.message}")
                        self.state.fixes_skipped += 1
                    else:
                        await self._apply_fix(action, file_path)
                else:
                    print(f"  ⏭️ {action.type.value}: {action.issue.message}")
                    self.state.fixes_skipped += 1
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.state.files_processed += 1
    
    async def _apply_fix(self, action: Action, file_path: Path) -> bool:
        print(f"  🔧 Fixing: {action.issue.message}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple fix for docstrings
            if action.strategy == FixStrategy.ADD_DOCSTRING:
                lines = content.split('\n')
                line_idx = action.issue.line - 1
                
                if 0 <= line_idx < len(lines):
                    indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
                    spaces = ' ' * (indent + 4)
                    func_name = action.issue.context.get('function', 'function')
                    docstring = f'{spaces}"""TODO: Add documentation for {func_name}."""'
                    lines.insert(line_idx + 1, docstring)
                    fixed_content = '\n'.join(lines)
                    
                    # Validate
                    try:
                        import ast
                        ast.parse(fixed_content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        
                        print(f"  ✅ Fix applied")
                        self.state.fixes_applied += 1
                        return True
                    except SyntaxError:
                        print(f"  ❌ Invalid syntax")
                        self.state.fixes_failed += 1
                        return False
            
            print(f"  ⏭️ No fix strategy available")
            self.state.fixes_skipped += 1
            return False
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.state.fixes_failed += 1
            return False
    
    def _generate_report(self) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print("📊 FINAL REPORT")
        print("=" * 60)
        
        # Severity breakdown
        severity_breakdown = {}
        issue_type_breakdown = {}
        for issue in self.all_issues:
            severity_breakdown[issue.severity.name] = severity_breakdown.get(issue.severity.name, 0) + 1
            issue_type_breakdown[issue.type] = issue_type_breakdown.get(issue.type, 0) + 1
        
        print(f"\n📈 Statistics:")
        print(f"  • Files analyzed: {self.state.files_processed}")
        print(f"  • Total issues: {self.state.total_issues_found}")
        print(f"  • Fixes applied: {self.state.fixes_applied}")
        print(f"  • Fixes failed: {self.state.fixes_failed}")
        print(f"  • Fixes skipped: {self.state.fixes_skipped}")
        print(f"  • Time: {self.state.elapsed_time:.1f}s")
        
        print(f"\n🐛 Issues by severity:")
        for sev, count in sorted(severity_breakdown.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {sev}: {count}")
        
        print(f"\n📋 Top issue types:")
        for issue_type, count in sorted(issue_type_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {issue_type}: {count}")
        
        return {
            'summary': {
                'files_analyzed': self.state.files_processed,
                'total_issues': self.state.total_issues_found,
                'fixes_applied': self.state.fixes_applied,
                'severity_breakdown': severity_breakdown,
                'issue_type_breakdown': issue_type_breakdown
            }
        }


# Simple test
if __name__ == "__main__":
    async def test():
        agent = CodingAssistantAgent({'workspace_dir': './test_workspace', 'dry_run': True})
        await agent.run('https://github.com/psf/requests')
    
    asyncio.run(test())