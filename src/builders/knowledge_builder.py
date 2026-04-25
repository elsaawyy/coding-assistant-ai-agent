"""Build structural understanding of the repository"""

import networkx as nx
from typing import Dict, List, Any
from collections import defaultdict

class KnowledgeBuilder:
    """Build repository knowledge graph"""
    
    def __init__(self):
        self.call_graph = nx.DiGraph()
        self.import_graph = nx.DiGraph()
        self.file_relationships = defaultdict(list)
        
    def build_from_analysis(self, analysis_results: List[Dict]):
        """Build knowledge from all analysis results"""
        
        for result in analysis_results:
            file_path = result['file']
            
            # Add imports
            for imp in result.get('imports', []):
                self.import_graph.add_edge(file_path, imp.module)
            
            # Add function calls
            for func in result.get('functions', []):
                self.call_graph.add_node(f"{file_path}:{func.name}")
                for called_func in func.calls:
                    self.call_graph.add_edge(
                        f"{file_path}:{func.name}",
                        called_func
                    )
    
    def find_impacted_files(self, changed_file: str) -> List[str]:
        """Find files that might be impacted by a change"""
        impacted = []
        
        # Files that import this file
        for edge in self.import_graph.edges():
            if edge[1] == changed_file:
                impacted.append(edge[0])
        
        return impacted
    
    def find_central_modules(self) -> List[str]:
        """Find most important modules"""
        centrality = nx.degree_centrality(self.import_graph)
        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]