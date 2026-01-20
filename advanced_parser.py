import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Any, Optional

class AdvancedAlteryxParser:
    """Advanced parser for Alteryx workflows with detailed tool configuration extraction"""
    
    # Comprehensive tool mapping
    TOOL_MAPPINGS = {
        # Input/Output Tools
        'Input Data': 'input_data',
        'Output Data': 'output_data',
        'Text Input': 'text_input',
        'Browse': 'browse',
        
        # Preparation Tools
        'Select': 'select',
        'Filter': 'filter',
        'Formula': 'formula',
        'Multi-Field Formula': 'multi_field_formula',
        'Sample': 'sample',
        'Record ID': 'record_id',
        'Auto Field': 'auto_field',
        'Data Cleansing': 'data_cleansing',
        'Imputation': 'imputation',
        
        # Join Tools
        'Join': 'join',
        'Join Multiple': 'join_multiple',
        'Union': 'union',
        'Find Replace': 'find_replace',
        'Append Fields': 'append_fields',
        
        # Parse Tools
        'Text to Columns': 'text_to_columns',
        'RegEx': 'regex',
        'DateTime': 'datetime',
        
        # Transform Tools
        'Summarize': 'summarize',
        'Cross Tab': 'cross_tab',
        'Transpose': 'transpose',
        'Running Total': 'running_total',
        'Sort': 'sort',
        'Unique': 'unique',
        
        # Documentation
        'Comment': 'comment',
        'Tool Container': 'container'
    }
    
    def __init__(self):
        self.tools: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
    def parse(self, xml_content: bytes) -> bool:
        """Parse Alteryx workflow XML"""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract metadata
            self._extract_metadata(root)
            
            # Extract all nodes (tools)
            self._extract_tools(root)
            
            # Extract connections
            self._extract_connections(root)
            
            return True
        except Exception as e:
            print(f"Parsing error: {e}")
            return False
    
    def _extract_metadata(self, root: ET.Element):
        """Extract workflow metadata"""
        self.metadata = {
            'version': root.get('version', 'Unknown'),
            'creation_date': None,
            'author': None,
            'description': None
        }
        
        # Try to extract additional metadata
        properties = root.find('.//Properties')
        if properties is not None:
            meta = properties.find('.//MetaInfo')
            if meta is not None:
                for child in meta:
                    if child.tag in ['Author', 'Description', 'CreationDate']:
                        self.metadata[child.tag.lower()] = child.text
    
    def _extract_tools(self, root: ET.Element):
        """Extract all tools from the workflow"""
        for node in root.findall('.//Node'):
            tool_info = self._parse_tool_node(node)
            if tool_info:
                self.tools.append(tool_info)
    
    def _parse_tool_node(self, node: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse individual tool node"""
        tool_id = node.get('ToolID')
        if not tool_id:
            return None
        
        # Get plugin information
        engine_settings = node.find('.//EngineSettings')
        plugin = engine_settings.get('EngineDll', '') if engine_settings is not None else ''
        macro = engine_settings.get('Macro', '') if engine_settings is not None else ''
        
        # Get GUI settings
        gui = self._extract_gui_settings(node)
        
        # Get properties
        properties = node.find('.//Properties')
        config = self._extract_detailed_config(properties) if properties is not None else {}
        
        # Identify tool type
        tool_type = self._identify_tool_type(plugin, macro, config)
        
        return {
            'id': tool_id,
            'type': tool_type,
            'plugin': plugin,
            'macro': macro,
            'config': config,
            'gui': gui,
            'annotation': self._extract_annotation(node)
        }
    
    def _identify_tool_type(self, plugin: str, macro: str, config: Dict) -> str:
        """Identify tool type from plugin and configuration"""
        # Check for specific tool indicators in config
        if 'File' in config:
            if 'FileName_Out' in config or any('output' in str(k).lower() for k in config.keys()):
                return 'output_data'
            else:
                return 'input_data'
        
        # Check plugin DLL
        if 'AlteryxBasePluginsEngine' in plugin:
            # Try to determine from config keys
            config_str = str(config).lower()
            if 'filter' in config_str:
                return 'filter'
            elif 'join' in config_str:
                return 'join'
            elif 'sort' in config_str:
                return 'sort'
            elif 'summarize' in config_str or 'groupby' in config_str:
                return 'summarize'
            elif 'formula' in config_str:
                return 'formula'
            elif 'select' in config_str:
                return 'select'
            elif 'unique' in config_str:
                return 'unique'
            elif 'sample' in config_str:
                return 'sample'
            elif 'recordid' in config_str:
                return 'record_id'
        
        elif 'AlteryxBasePluginsGui' in plugin:
            if 'browse' in plugin.lower():
                return 'browse'
            elif 'textinput' in plugin.lower():
                return 'text_input'
        
        # Check for macros
        if macro:
            return f'macro:{macro}'
        
        return 'unknown'
    
    def _extract_detailed_config(self, properties: ET.Element) -> Dict[str, Any]:
        """Extract detailed configuration from properties"""
        config = {}
        
        configuration = properties.find('.//Configuration')
        if configuration is None:
            return config
        
        # Recursively extract all configuration elements
        self._recursive_config_extract(configuration, config)
        
        return config
    
    def _recursive_config_extract(self, element: ET.Element, config: Dict, prefix: str = ''):
        """Recursively extract configuration from XML element"""
        for child in element:
            key = f"{prefix}{child.tag}" if prefix else child.tag
            
            # If element has children, recurse
            if len(child) > 0:
                sub_config = {}
                self._recursive_config_extract(child, sub_config, '')
                config[key] = sub_config
            else:
                # Store text or attributes
                if child.text and child.text.strip():
                    config[key] = child.text.strip()
                elif child.attrib:
                    config[key] = child.attrib
                else:
                    config[key] = None
    
    def _extract_gui_settings(self, node: ET.Element) -> Dict[str, Any]:
        """Extract GUI settings"""
        gui_settings = {}
        
        gui = node.find('.//GuiSettings')
        if gui is not None:
            position = gui.find('.//Position')
            if position is not None:
                gui_settings['position'] = {
                    'x': float(position.get('x', 0)),
                    'y': float(position.get('y', 0))
                }
        
        return gui_settings
    
    def _extract_annotation(self, node: ET.Element) -> Optional[str]:
        """Extract tool annotation/comment"""
        properties = node.find('.//Properties')
        if properties is not None:
            annotation = properties.find('.//Annotation')
            if annotation is not None:
                name = annotation.find('.//Name')
                if name is not None and name.text:
                    return name.text.strip()
        return None
    
    def _extract_connections(self, root: ET.Element):
        """Extract connections between tools"""
        for connection in root.findall('.//Connection'):
            origin = connection.find('.//Origin')
            destination = connection.find('.//Destination')
            
            if origin is not None and destination is not None:
                conn_info = {
                    'name': connection.get('name', 'Output'),
                    'source': origin.text.strip() if origin.text else '',
                    'destination': destination.text.strip() if destination.text else ''
                }
                self.connections.append(conn_info)
    
    def get_execution_order(self) -> List[str]:
        """Determine tool execution order using topological sort"""
        # Build adjacency list
        graph = {}
        in_degree = {}
        
        for tool in self.tools:
            tool_id = tool['id']
            graph[tool_id] = []
            in_degree[tool_id] = 0
        
        for conn in self.connections:
            source = conn['source']
            dest = conn['destination']
            if source in graph and dest in graph:
                graph[source].append(dest)
                in_degree[dest] = in_degree.get(dest, 0) + 1
        
        # Topological sort using Kahn's algorithm
        queue = [tool_id for tool_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration by ID"""
        for tool in self.tools:
            if tool['id'] == tool_id:
                return tool
        return None
    
    def get_source_tools(self, tool_id: str) -> List[str]:
        """Get all tools that feed into the specified tool"""
        sources = []
        for conn in self.connections:
            if conn['destination'] == tool_id:
                sources.append(conn['source'])
        return sources
    
    def get_destination_tools(self, tool_id: str) -> List[str]:
        """Get all tools that this tool feeds into"""
        destinations = []
        for conn in self.connections:
            if conn['source'] == tool_id:
                destinations.append(conn['destination'])
        return destinations
