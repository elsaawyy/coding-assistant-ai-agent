"""Fix generator for all issue types"""

import re
import ast
from pathlib import Path
from typing import Optional, List, Tuple

class FixGenerator:
    """Generate fixes for all detected issues"""
    
    def __init__(self):
        self.fix_count = 0
        self.fix_stats = {
            'docstring_added': 0,
            'complexity_reduced': 0,
            'split_suggested': 0
        }
    
    async def generate_fix(self, file_path: Path, issue, strategy: str) -> Optional[str]:
        """Generate a fix based on strategy"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        line_idx = issue.line - 1
        
        if line_idx < 0 or line_idx >= len(lines):
            return None
        
        # Handle different fix strategies
        if strategy == 'add_docstring':
            return self._add_docstring(lines, line_idx, issue)
        
        elif strategy == 'simplify_logic':
            return self._simplify_nested_logic(content, issue)
        
        elif strategy == 'split_function':
            return self._add_split_comment(lines, line_idx, issue)
        
        elif strategy == 'extract_method':
            return self._suggest_extraction(lines, line_idx, issue)
        
        elif strategy == 'manual_review':
            return self._add_review_comment(lines, line_idx, issue)
        
        return None
    
    def _add_docstring(self, lines: List[str], line_idx: int, issue) -> Optional[str]:
        """Add docstring to function"""
        func_line = lines[line_idx]
        
        # Skip if already has docstring
        if line_idx + 1 < len(lines) and '"""' in lines[line_idx + 1]:
            return None
        
        # Get function name
        func_match = re.search(r'def\s+(\w+)', func_line)
        func_name = func_match.group(1) if func_match else 'function'
        
        # Calculate indentation
        indent = len(func_line) - len(func_line.lstrip())
        spaces = ' ' * (indent + 4)
        
        # Create docstring
        docstring = f'{spaces}"""TODO: Add documentation for {func_name}.'
        
        # Add parameter info if available
        param_match = re.search(r'\((.*?)\)', func_line)
        if param_match and param_match.group(1):
            params = [p.strip().split(':')[0].split('=')[0].strip() 
                     for p in param_match.group(1).split(',')]
            params = [p for p in params if p and p not in ['self', 'cls']]
            
            if params:
                docstring += f'\n{spaces}    \n{spaces}    Args:'
                for param in params[:3]:  # Limit to 3 params
                    docstring += f'\n{spaces}        {param}: TODO'
        
        docstring += f'\n{spaces}    \n{spaces}    Returns: TODO'
        docstring += '\n{spaces}"""'
        
        # Insert docstring
        lines.insert(line_idx + 1, docstring)
        self.fix_stats['docstring_added'] += 1
        return '\n'.join(lines)
    
    def _simplify_nested_logic(self, content: str, issue) -> Optional[str]:
        """Simplify nested if statements"""
        original = content
        
        # Pattern 1: Nested ifs
        # if condition1:\n    if condition2:
        pattern1 = r'(\s+)if\s+(.*?):\s*\n\s+\1\s+if\s+(.*?):'
        replacement1 = r'\1if \2 and \3:'
        
        fixed = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: if condition: return True else: return False
        pattern2 = r'if\s+(.*?):\s*\n\s+return\s+True\s*\n\s*else:\s*\n\s+return\s+False'
        replacement2 = r'return \1'
        
        fixed = re.sub(pattern2, replacement2, fixed, flags=re.DOTALL)
        
        if fixed != content:
            self.fix_stats['complexity_reduced'] += 1
            return fixed
        
        return None
    
    def _add_split_comment(self, lines: List[str], line_idx: int, issue) -> Optional[str]:
        """Add comment suggesting function split"""
        func_line = lines[line_idx]
        func_match = re.search(r'def\s+(\w+)', func_line)
        
        if not func_match:
            return None
        
        func_name = func_match.group(1)
        indent = len(func_line) - len(func_line.lstrip())
        spaces = ' ' * (indent + 4)
        
        # Find function end
        end_idx = self._find_function_end(lines, line_idx + 1)
        line_count = end_idx - line_idx
        
        # Add suggestion comment
        comment = f'{spaces}# TODO: This function is too long ({line_count} lines).'
        comment += f'\n{spaces}# Consider extracting logical blocks into separate functions:'
        
        # Find logical blocks
        blocks = self._find_logical_blocks(lines[line_idx + 1:end_idx], indent + 4)
        for i, block_start in enumerate(blocks[:3]):
            comment += f'\n{spaces}#   - _extract_{func_name}_part_{i+1}()  (line {line_idx + 2 + block_start})'
        
        lines.insert(line_idx + 2, comment)
        self.fix_stats['split_suggested'] += 1
        return '\n'.join(lines)
    
    def _suggest_extraction(self, lines: List[str], line_idx: int, issue) -> Optional[str]:
        """Suggest extracting a method"""
        param_match = re.search(r'def\s+(\w+)\((.*?)\)', lines[line_idx])
        
        if param_match:
            func_name = param_match.group(1)
            params = param_match.group(2)
            
            indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
            spaces = ' ' * (indent + 4)
            
            comment = f'{spaces}# TODO: Too many parameters ({len(params.split(",")) if params else 0})'
            comment += f'\n{spaces}# Consider using a configuration object or splitting the function'
            
            lines.insert(line_idx + 1, comment)
            return '\n'.join(lines)
        
        return None
    
    def _add_review_comment(self, lines: List[str], line_idx: int, issue) -> Optional[str]:
        """Add review comment for critical issues"""
        indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
        spaces = ' ' * indent
        
        comment = f'{spaces}# REVIEW: {issue.message}'
        comment += f'\n{spaces}# Suggestion: {issue.suggestion}'
        
        lines.insert(line_idx, comment)
        return '\n'.join(lines)
    
    def _find_function_end(self, lines: List[str], start: int) -> int:
        """Find the end line of a function"""
        if start >= len(lines):
            return start
        
        base_indent = len(lines[start]) - len(lines[start].lstrip()) if lines[start].strip() else 0
        
        for i in range(start, len(lines)):
            line = lines[i]
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= base_indent:
                    return i - 1
        
        return len(lines) - 1
    
    def _find_logical_blocks(self, lines: List[str], base_indent: int) -> List[int]:
        """Find logical blocks (if, for, while) in function body"""
        blocks = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Check for control flow statements
            if indent == base_indent and re.match(r'\s*(if|for|while|with|try)', line):
                blocks.append(i)
        
        return blocks
    
    def get_stats(self) -> dict:
        """Get fix statistics"""
        return self.fix_stats.copy()