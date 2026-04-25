import ast
from typing import Dict, List, Set, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    complexity: int
    parameters: List[str]
    returns: str
    docstring: str
    calls: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)

@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo]
    attributes: List[str]
    base_classes: List[str]
    start_line: int
    end_line: int

@dataclass
class ImportInfo:
    module: str
    names: List[str]
    is_from_import: bool

class PythonAnalyzer:
    """AST-based code analyzer for Python"""
    
    def __init__(self):
        self.imports = []
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            visitor = _CodeVisitor()
            visitor.visit(tree)
            
            return {
                'file': str(file_path),
                'functions': visitor.functions,
                'classes': visitor.classes,
                'imports': visitor.imports,
                'lines': len(content.splitlines()),
                'characters': len(content),
                'complexity': self._calculate_file_complexity(visitor.functions),
                'has_docstring': bool(ast.get_docstring(tree))
            }
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return {
                'file': str(file_path),
                'error': str(e),
                'lines': 0,
                'functions': [],
                'classes': [],
                'imports': []
            }
    
    def _calculate_file_complexity(self, functions: List[FunctionInfo]) -> float:
        """Calculate average cyclomatic complexity"""
        if not functions:
            return 0.0
        return sum(f.complexity for f in functions) / len(functions)

class _CodeVisitor(ast.NodeVisitor):
    """AST visitor to extract code information"""
    
    def __init__(self):
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.imports: List[ImportInfo] = []
        self.current_class: Optional[str] = None
        
    def visit_FunctionDef(self, node):
        """Extract function information"""
        # Skip methods if we want to track them separately
        func_info = FunctionInfo(
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            complexity=self._calculate_complexity(node),
            parameters=[arg.arg for arg in node.args.args],
            returns=self._get_return_type(node),
            docstring=ast.get_docstring(node) or "",
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
        
        # Find function calls
        calls_visitor = _CallVisitor()
        calls_visitor.visit(node)
        func_info.calls = list(set(calls_visitor.calls))
        
        self.functions.append(func_info)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        """Handle async functions"""
        func_info = FunctionInfo(
            name=f"async_{node.name}",
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            complexity=self._calculate_complexity(node),
            parameters=[arg.arg for arg in node.args.args],
            returns=self._get_return_type(node),
            docstring=ast.get_docstring(node) or "",
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
        self.functions.append(func_info)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Extract class information"""
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(FunctionInfo(
                    name=item.name,
                    start_line=item.lineno,
                    end_line=item.end_lineno or item.lineno,
                    complexity=self._calculate_complexity(item),
                    parameters=[arg.arg for arg in item.args.args],
                    returns=self._get_return_type(item),
                    docstring=ast.get_docstring(item) or "",
                    decorators=[self._get_decorator_name(d) for d in item.decorator_list]
                ))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
                        
        class_info = ClassInfo(
            name=node.name,
            methods=methods,
            attributes=attributes,
            base_classes=[self._get_base_class_name(base) for base in node.bases],
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno
        )
        
        self.classes.append(class_info)
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None
        
    def visit_Import(self, node):
        """Handle import statements"""
        for alias in node.names:
            self.imports.append(ImportInfo(
                module=alias.name,
                names=[alias.name],
                is_from_import=False
            ))
            
    def visit_ImportFrom(self, node):
        """Handle from ... import ... statements"""
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.imports.append(ImportInfo(
            module=module,
            names=names,
            is_from_import=True
        ))
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
                
        return complexity
    
    def _get_return_type(self, node) -> str:
        """Extract return type annotation"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return f"{node.returns.value.id}.{node.returns.attr}" if hasattr(node.returns.value, 'id') else str(node.returns)
        return "Any"
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return "unknown"
    
    def _get_base_class_name(self, base) -> str:
        """Extract base class name"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return "object"

class _CallVisitor(ast.NodeVisitor):
    """Visitor to find function calls"""
    
    def __init__(self):
        self.calls = []
        
    def visit_Call(self, node):
        """Extract called function names"""
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)