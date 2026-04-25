from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

class ActionType(Enum):
    FIX = "fix"
    SKIP = "skip"
    REPORT = "report"
    REVIEW = "review"

class FixStrategy(Enum):
    AUTO_REFACTOR = "auto_refactor"
    ADD_DOCSTRING = "add_docstring"
    SPLIT_FUNCTION = "split_function"
    SIMPLIFY_LOGIC = "simplify_logic"
    EXTRACT_METHOD = "extract_method"
    MANUAL_REVIEW = "manual_review"

@dataclass
class Action:
    type: ActionType
    priority: int
    issue: Any
    strategy: FixStrategy
    confidence: float = 1.0
    retry_count: int = 0

@dataclass
class DecisionContext:
    file_path: str
    file_importance: int
    issues_in_file: int
    fixes_applied_in_file: int

class DecisionEngine:
    """Core decision-making logic for the agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.action_history = []
        self.issue_attempts = defaultdict(int)
        self.issue_success_rate = defaultdict(float)
        
        # Configuration parameters
        self.min_severity = config.get('min_severity', 1)
        self.max_fixes_per_run = config.get('max_fixes_per_run', 20)
        self.max_retries = config.get('max_retries', 3)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
    def prioritize_issues(self, issues: List, file_path: str) -> List[Action]:
        """Prioritize issues based on multiple factors"""
        actions = []
        context = self._get_context(file_path)
        
        for issue in issues:
            # Skip low severity issues if below threshold
            if issue.severity.value < self.min_severity:
                continue
                
            # Calculate priority score (higher is more important)
            priority_score = self._calculate_priority_score(issue, context)
            
            # Determine if we should fix or skip
            action_type = self._decide_action(issue, context)
            
            # Select fix strategy based on issue type
            strategy = self._select_strategy(issue)
            
            # Calculate confidence in successful fix
            confidence = self._calculate_confidence(issue)
            
            actions.append(Action(
                type=action_type,
                priority=priority_score,
                issue=issue,
                strategy=strategy,
                confidence=confidence,
                retry_count=self.issue_attempts[self._get_issue_key(issue)]
            ))
        
        # Sort by priority (highest first)
        actions.sort(key=lambda x: x.priority, reverse=True)
        
        # Limit actions per file if configured
        max_per_file = self.config.get('max_actions_per_file', 10)
        return actions[:max_per_file]
    
    def _calculate_priority_score(self, issue, context: DecisionContext) -> int:
        """Calculate priority score based on multiple factors"""
        score = 0
        
        # Base severity score (0-4)
        score += issue.severity.value * 25
        
        # File importance bonus (0-20)
        score += context.file_importance * 4
        
        # Penalty for retries (negative)
        retries = self.issue_attempts[self._get_issue_key(issue)]
        score -= retries * 5
        
        # Bonus for high success rate issues
        success_rate = self.issue_success_rate.get(issue.type, 0.5)
        score += int(success_rate * 10)
        
        # Penalty if file already has many fixes
        if context.fixes_applied_in_file > 5:
            score -= 10
            
        return max(0, score)
    
    def _decide_action(self, issue, context: DecisionContext) -> ActionType:
        """Decide whether to fix, skip, report, or request review"""
        
        # Critical issues always get fixed
        if issue.severity.value >= 3:
            return ActionType.FIX
        
        # Check retry limit
        retries = self.issue_attempts[self._get_issue_key(issue)]
        if retries >= self.max_retries:
            return ActionType.SKIP
        
        # Check if we've reached max fixes for this run
        total_fixes = sum(1 for a in self.action_history if a.type == ActionType.FIX)
        if total_fixes >= self.max_fixes_per_run:
            return ActionType.REPORT
        
        # Low confidence issues go to manual review
        confidence = self._calculate_confidence(issue)
        if confidence < self.confidence_threshold:
            return ActionType.REVIEW
        
        # Default to fix for medium severity
        if issue.severity.value >= 2:
            return ActionType.FIX
        
        # Skip low severity by default
        return ActionType.SKIP
    
    def _select_strategy(self, issue) -> FixStrategy:
        """Select fix strategy based on issue type"""
        strategy_map = {
            'long_function': FixStrategy.SPLIT_FUNCTION,
            'high_complexity': FixStrategy.SIMPLIFY_LOGIC,
            'very_high_complexity': FixStrategy.MANUAL_REVIEW,
            'no_docstring': FixStrategy.ADD_DOCSTRING,
            'too_many_parameters': FixStrategy.EXTRACT_METHOD,
            'duplicate_code': FixStrategy.EXTRACT_METHOD,
            'empty_class': FixStrategy.AUTO_REFACTOR,
            'large_file': FixStrategy.MANUAL_REVIEW
        }
        return strategy_map.get(issue.type, FixStrategy.MANUAL_REVIEW)
    
    def _calculate_confidence(self, issue) -> float:
        """Calculate confidence in successfully fixing this issue"""
        base_confidence = {
            'no_docstring': 0.95,
            'long_function': 0.75,
            'high_complexity': 0.65,
            'too_many_parameters': 0.70,
            'duplicate_code': 0.60,
            'empty_class': 0.85
        }.get(issue.type, 0.50)
        
        # Adjust based on historical success rate
        historical_success = self.issue_success_rate.get(issue.type, 0.5)
        
        # Weighted average (70% base, 30% historical)
        confidence = (base_confidence * 0.7) + (historical_success * 0.3)
        
        # Reduce confidence if retrying
        retries = self.issue_attempts[self._get_issue_key(issue)]
        confidence *= (1 - (retries * 0.1))
        
        return round(min(1.0, max(0.0, confidence)), 2)
    
    def _get_context(self, file_path: str) -> DecisionContext:
        """Get decision context for a file"""
        # Calculate file importance based on name patterns
        importance = 1
        important_patterns = ['main', 'core', 'base', 'utils', 'common', 'models']
        for pattern in important_patterns:
            if pattern in file_path.lower():
                importance = 5
                break
    
        # Count issues in this file from history
        issues_in_file = 0
        fixes_in_file = 0
    
        for item in self.action_history:
            if isinstance(item, dict):
                # Handle dict items
                if 'issue' in item and hasattr(item['issue'], 'file'):
                    if item['issue'].file == file_path:
                        issues_in_file += 1
                elif 'issue_key' in item and file_path in item['issue_key']:
                    issues_in_file += 1
            else:
                # Handle Action objects
                if hasattr(item, 'issue') and hasattr(item.issue, 'file'):
                    if item.issue.file == file_path:
                        issues_in_file += 1
                        if hasattr(item, 'type') and item.type == ActionType.FIX:
                            fixes_in_file += 1
    
        return DecisionContext(
            file_path=file_path,
            file_importance=importance,
            issues_in_file=issues_in_file,
            fixes_applied_in_file=fixes_in_file
        )
 
    
    def _get_issue_key(self, issue) -> str:
        """Generate unique key for an issue"""
        return f"{issue.file}:{issue.line}:{issue.type}"
    
    def record_attempt(self, issue, success: bool, fix_time: float = 0):
        """Record a fix attempt for learning"""
        key = self._get_issue_key(issue)
        self.issue_attempts[key] += 1
    
        #  Update success rate for issue type
        type_key = issue.type
        total_attempts = 0
        total_successes = 0
    
        # Safely count attempts from action_history
        for item in self.action_history:
            if isinstance(item, dict):
                if item.get('type') == type_key:
                    total_attempts += 1
                    if item.get('success', False):
                        total_successes += 1
            else:
                # Handle if it's an Action object
                if hasattr(item, 'issue') and item.issue.type == type_key:
                    total_attempts += 1
                    if hasattr(item, 'success') and item.success:
                        total_successes += 1
    
        if total_attempts > 0:
            self.issue_success_rate[type_key] = total_successes / total_attempts
    
        # Record action as dict to avoid type issues
        self.action_history.append({
            'issue_key': key,
            'type': issue.type,
            'success': success,
            'fix_time': fix_time,
            'severity': issue.severity.value
        })
    
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        total_attempts = len(self.action_history)
        successful_fixes = sum(1 for a in self.action_history if a.get('success', False))
        
        return {
            'total_attempts': total_attempts,
            'successful_fixes': successful_fixes,
            'success_rate': successful_fixes / total_attempts if total_attempts > 0 else 0,
            'issue_attempts': dict(self.issue_attempts),
            'issue_success_rates': dict(self.issue_success_rate)
        }
    
    def should_continue(self) -> bool:
        """Determine if the agent should continue processing"""
        total_fixes = sum(1 for a in self.action_history if a.get('success', False))
        
        # Stop if we've reached max fixes
        if total_fixes >= self.max_fixes_per_run:
            return False
        
        # Stop if recent fix rate is very low (less than 20% over last 10 attempts)
        recent_attempts = self.action_history[-10:]
        if len(recent_attempts) >= 10:
            recent_successes = sum(1 for a in recent_attempts if a.get('success', False))
            if recent_successes < 2:
                return False
        
        return True