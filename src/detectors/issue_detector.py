from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class Severity(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0
    
    def __str__(self):
        return self.name
    
    @property
    def emoji(self):
        emojis = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🔵',
            'INFO': '⚪'
        }
        return emojis.get(self.name, '⚪')

@dataclass
class Issue:
    type: str
    severity: Severity
    file: str
    line: int
    message: str
    suggestion: str
    context: Dict[str, Any]
    
    def to_dict(self):
        return {
            'type': self.type,
            'severity': self.severity.name,
            'severity_value': self.severity.value,
            'file': self.file,
            'line': self.line,
            'message': self.message,
            'suggestion': self.suggestion,
            'context': self.context
        }

class IssueDetector:
    """Rule-based issue detection engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules = self._load_rules()
        
    def _load_rules(self) -> List[Dict]:
        """Load detection rules with their check functions"""
        return [
            {
                'name': 'long_function',
                'severity': Severity.MEDIUM,
                'message': 'Function is too long',
                'suggestion': 'Break down into smaller functions (max 50 lines recommended)',
                'check': lambda func, **kwargs: func.end_line - func.start_line > 50
            },
            {
                'name': 'high_complexity',
                'severity': Severity.HIGH,
                'message': 'High cyclomatic complexity',
                'suggestion': 'Simplify control flow or split function into smaller parts',
                'check': lambda func, **kwargs: func.complexity > 10
            },
            {
                'name': 'very_high_complexity',
                'severity': Severity.CRITICAL,
                'message': 'Very high cyclomatic complexity',
                'suggestion': 'Function is too complex. Refactor immediately!',
                'check': lambda func, **kwargs: func.complexity > 20
            },
            {
                'name': 'no_docstring',
                'severity': Severity.LOW,
                'message': 'Missing docstring',
                'suggestion': 'Add documentation explaining function purpose, parameters, and return value',
                'check': lambda func, **kwargs: not func.docstring
            },
            {
                'name': 'too_many_parameters',
                'severity': Severity.MEDIUM,
                'message': 'Too many parameters',
                'suggestion': 'Use configuration object or split function (max 5 parameters recommended)',
                'check': lambda func, **kwargs: len(func.parameters) > 5
            },
            {
                'name': 'too_many_returns',
                'severity': Severity.LOW,
                'message': 'Multiple return statements',
                'suggestion': 'Consider simplifying control flow',
                'check': self._check_multiple_returns
            },
            {
                'name': 'empty_except',
                'severity': Severity.HIGH,
                'message': 'Empty except block',
                'suggestion': 'Either handle the exception properly or log it',
                'check': self._check_empty_except
            },
            {
                'name': 'todo_comment',
                'severity': Severity.INFO,
                'message': 'TODO comment found',
                'suggestion': 'Address or track this TODO item',
                'check': self._check_todo_comment
            }
        ]
    
    def detect_issues(self, analysis: Dict[str, Any]) -> List[Issue]:
        """Detect issues in analyzed code"""
        issues = []
        
        # Check functions
        for func in analysis.get('functions', []):
            for rule in self.rules:
                try:
                    if rule['check'](func, content=analysis.get('content', '')):
                        issues.append(Issue(
                            type=rule['name'],
                            severity=rule['severity'],
                            file=analysis['file'],
                            line=func.start_line,
                            message=rule['message'],
                            suggestion=rule['suggestion'],
                            context={
                                'function': func.name,
                                'lines': func.end_line - func.start_line,
                                'complexity': func.complexity,
                                'parameters': func.parameters
                            }
                        ))
                except Exception as e:
                    print(f"Error checking rule {rule['name']}: {e}")
        
        # Check classes
        for cls in analysis.get('classes', []):
            if not cls.methods and not cls.attributes:
                issues.append(Issue(
                    type='empty_class',
                    severity=Severity.LOW,
                    file=analysis['file'],
                    line=cls.start_line,
                    message='Empty class',
                    suggestion='Either add functionality or remove the class',
                    context={'class': cls.name}
                ))
        
        # Check file-level issues
        if analysis.get('lines', 0) > 500:
            issues.append(Issue(
                type='large_file',
                severity=Severity.MEDIUM,
                file=analysis['file'],
                line=1,
                message=f'Large file: {analysis["lines"]} lines',
                suggestion='Split into multiple modules',
                context={'lines': analysis['lines']}
            ))
        
        # Find duplicate code patterns
        duplicates = self._find_duplicate_patterns(analysis.get('functions', []))
        for dup in duplicates:
            issues.append(Issue(
                type='duplicate_code',
                severity=Severity.MEDIUM,
                file=analysis['file'],
                line=dup[0].start_line,
                message='Duplicate code pattern detected',
                suggestion='Extract common functionality into a shared function',
                context={'functions': [f.name for f in dup]}
            ))
        
        # Sort by severity (highest first)
        issues.sort(key=lambda x: x.severity.value, reverse=True)
        return issues
    
    def _check_multiple_returns(self, func, **kwargs) -> bool:
        """Check for functions with many return statements"""
        # This would need access to the function's AST
        # Simplified for now
        return False
    
    def _check_empty_except(self, func, **kwargs) -> bool:
        """Check for empty except blocks"""
        # This would need access to the function's AST
        # Simplified for now
        return False
    
    def _check_todo_comment(self, func, **kwargs) -> bool:
        """Check for TODO comments in function"""
        content = kwargs.get('content', '')
        if content:
            lines = content.split('\n')
            start = max(0, func.start_line - 1)
            end = min(len(lines), func.end_line)
            for i in range(start, end):
                if 'TODO' in lines[i] or 'FIXME' in lines[i]:
                    return True
        return False
    
    def _find_duplicate_patterns(self, functions) -> List[List]:
        """Find duplicate code patterns between functions"""
        duplicates = []
        # This would implement actual code similarity detection
        # Simplified for now
        return duplicates
    
    def get_statistics(self, issues: List[Issue]) -> Dict[str, Any]:
        """Get statistics about detected issues"""
        stats = {
            'total': len(issues),
            'by_severity': {},
            'by_type': {}
        }
        
        for issue in issues:
            severity_name = issue.severity.name
            stats['by_severity'][severity_name] = stats['by_severity'].get(severity_name, 0) + 1
            stats['by_type'][issue.type] = stats['by_type'].get(issue.type, 0) + 1
        
        return stats