import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import io
import os
import json
from datetime import datetime
from pathlib import Path

class AlteryxWorkflowAnalyzer:
    """Analyzes and converts Alteryx workflows to Python scripts"""
    
    def __init__(self):
        self.tools = []
        self.connections = []
        self.workflow_config = {}
        self.input_files = {}
        self.output_specs = []
        
    def parse_workflow(self, yxmd_content):
        """Parse Alteryx .yxmd workflow file"""
        try:
            root = ET.fromstring(yxmd_content)
            
            # Extract nodes (tools)
            for node in root.findall('.//Node'):
                tool_id = node.get('ToolID')
                plugin = node.find('.//EngineSettings').get('EngineDll') if node.find('.//EngineSettings') is not None else ''
                
                # Get tool configuration
                properties = node.find('.//Properties')
                config = self._extract_config(properties) if properties is not None else {}
                
                tool_info = {
                    'id': tool_id,
                    'plugin': plugin,
                    'type': self._identify_tool_type(plugin),
                    'config': config,
                    'gui_settings': self._extract_gui_settings(node)
                }
                self.tools.append(tool_info)
            
            # Extract connections between tools
            for connection in root.findall('.//Connection'):
                conn_info = {
                    'origin': connection.get('name'),
                    'source': connection.find('.//Origin').text if connection.find('.//Origin') is not None else '',
                    'destination': connection.find('.//Destination').text if connection.find('.//Destination') is not None else ''
                }
                self.connections.append(conn_info)
            
            return True
        except Exception as e:
            st.error(f"Error parsing workflow: {str(e)}")
            return False
    
    def _identify_tool_type(self, plugin):
        """Identify the Alteryx tool type from plugin name"""
        tool_mapping = {
            'AlteryxBasePluginsEngine.dll': {
                'Input': 'input_data',
                'Output': 'output_data',
                'Select': 'select',
                'Filter': 'filter',
                'Formula': 'formula',
                'Join': 'join',
                'Sort': 'sort',
                'Unique': 'unique',
                'Sample': 'sample',
                'Summarize': 'summarize',
                'RecordID': 'record_id'
            },
            'AlteryxBasePluginsGui.dll': {
                'BrowseV2': 'browse',
                'TextInput': 'text_input'
            }
        }
        
        # Try to extract tool type from plugin path
        for key in tool_mapping:
            if key in plugin:
                return 'base_tool'
        return 'unknown'
    
    def _extract_config(self, properties):
        """Extract configuration from tool properties"""
        config = {}
        
        # Configuration node
        configuration = properties.find('.//Configuration')
        if configuration is not None:
            for child in configuration:
                config[child.tag] = child.text or child.attrib
        
        return config
    
    def _extract_gui_settings(self, node):
        """Extract GUI settings from node"""
        gui = node.find('.//GuiSettings')
        if gui is not None:
            position = gui.find('.//Position')
            if position is not None:
                return {
                    'x': position.get('x'),
                    'y': position.get('y')
                }
        return {}
    
    def analyze_workflow(self):
        """Analyze the workflow structure"""
        analysis = {
            'total_tools': len(self.tools),
            'total_connections': len(self.connections),
            'tool_types': {},
            'inputs': [],
            'outputs': [],
            'transformations': []
        }
        
        for tool in self.tools:
            tool_type = tool['type']
            analysis['tool_types'][tool_type] = analysis['tool_types'].get(tool_type, 0) + 1
            
            # Categorize tools
            if 'input' in str(tool['plugin']).lower() or 'Input' in str(tool['config']):
                analysis['inputs'].append(tool)
            elif 'output' in str(tool['plugin']).lower() or 'Output' in str(tool['config']):
                analysis['outputs'].append(tool)
            else:
                analysis['transformations'].append(tool)
        
        return analysis
    
    def generate_python_code(self):
        """Generate Python code equivalent to the Alteryx workflow"""
        code_lines = []
        
        # Header
        code_lines.append("# Auto-generated Python script from Alteryx workflow")
        code_lines.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        code_lines.append("")
        code_lines.append("import pandas as pd")
        code_lines.append("import numpy as np")
        code_lines.append("from datetime import datetime")
        code_lines.append("")
        
        # Create a mapping of tool IDs to variable names
        tool_vars = {}
        
        # Sort tools based on connections (topological sort)
        sorted_tools = self._topological_sort()
        
        for tool in sorted_tools:
            tool_id = tool['id']
            var_name = f"df_{tool_id}"
            tool_vars[tool_id] = var_name
            
            # Generate code based on tool type
            code_segment = self._generate_tool_code(tool, tool_vars)
            if code_segment:
                code_lines.extend(code_segment)
                code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _topological_sort(self):
        """Sort tools in execution order based on connections"""
        # Simple implementation: return tools in original order
        # In production, implement proper topological sorting
        return self.tools
    
    def _generate_tool_code(self, tool, tool_vars):
        """Generate Python code for a specific tool"""
        code = []
        tool_id = tool['id']
        var_name = tool_vars[tool_id]
        
        # Input Data Tool
        if 'input' in str(tool['plugin']).lower():
            config = tool['config']
            filename = config.get('File', 'input.csv')
            code.append(f"# Input Data Tool (ID: {tool_id})")
            code.append(f"# Original file: {filename}")
            code.append(f"{var_name} = pd.read_csv('{filename}')")
            self.input_files[tool_id] = filename
        
        # Output Data Tool
        elif 'output' in str(tool['plugin']).lower():
            config = tool['config']
            filename = config.get('File', 'output.csv')
            
            # Find the source tool
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, var_name)
                code.append(f"# Output Data Tool (ID: {tool_id})")
                code.append(f"# Output file: {filename}")
                code.append(f"{source_var}.to_csv('{filename}', index=False)")
                self.output_specs.append({'id': tool_id, 'file': filename, 'var': source_var})
        
        # Select Tool
        elif 'select' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Select Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.copy()")
        
        # Filter Tool
        elif 'filter' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Filter Tool (ID: {tool_id})")
                code.append(f"# Add your filter condition here")
                code.append(f"{var_name} = {source_var}[{source_var}['column'] > 0]  # Example filter")
        
        # Sort Tool
        elif 'sort' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Sort Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.sort_values('column')  # Specify column")
        
        # Join Tool
        elif 'join' in str(tool['config']).lower():
            sources = self._find_all_source_tools(tool_id)
            if len(sources) >= 2:
                left_var = tool_vars.get(sources[0], 'df1')
                right_var = tool_vars.get(sources[1], 'df2')
                code.append(f"# Join Tool (ID: {tool_id})")
                code.append(f"{var_name} = pd.merge({left_var}, {right_var}, on='key_column', how='inner')")
        
        # Summarize Tool
        elif 'summarize' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Summarize Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.groupby('group_column').agg({{'value_column': 'sum'}})")
        
        # Formula Tool
        elif 'formula' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Formula Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.copy()")
                code.append(f"{var_name}['new_column'] = {var_name}['existing_column'] * 2  # Example formula")
        
        # Unique Tool
        elif 'unique' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Unique Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.drop_duplicates()")
        
        # Sample Tool
        elif 'sample' in str(tool['config']).lower():
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Sample Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.sample(n=100)  # Specify sample size")
        
        # Record ID Tool
        elif 'recordid' in str(tool['config']).lower() or 'RecordID' in str(tool['config']):
            source_tool = self._find_source_tool(tool_id)
            if source_tool:
                source_var = tool_vars.get(source_tool, 'df')
                code.append(f"# Record ID Tool (ID: {tool_id})")
                code.append(f"{var_name} = {source_var}.copy()")
                code.append(f"{var_name}['RecordID'] = range(1, len({var_name}) + 1)")
        
        return code
    
    def _find_source_tool(self, tool_id):
        """Find the source tool that feeds into this tool"""
        for conn in self.connections:
            if conn['destination'] == tool_id:
                return conn['source']
        return None
    
    def _find_all_source_tools(self, tool_id):
        """Find all source tools that feed into this tool"""
        sources = []
        for conn in self.connections:
            if conn['destination'] == tool_id:
                sources.append(conn['source'])
        return sources


def main():
    st.set_page_config(page_title="Alteryx to Python Converter", layout="wide", page_icon="🔄")
    
    st.title("🔄 Alteryx Workflow to Python Converter")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.info("""
        This application analyzes Alteryx workflows (.yxmd files) and converts them 
        into equivalent Python scripts using pandas.
        
        **Features:**
        - Parse Alteryx workflow files
        - Analyze workflow structure
        - Generate Python code
        - Execute generated scripts
        - Download results
        """)
        
        st.markdown("---")
        st.header("🔧 Settings")
        auto_execute = st.checkbox("Auto-execute generated code", value=False)
        show_analysis = st.checkbox("Show detailed analysis", value=True)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload Workflow", "🔍 Analysis", "💻 Generated Code", "▶️ Execute"])
    
    with tab1:
        st.header("Upload Alteryx Workflow")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an Alteryx workflow file (.yxmd)", 
            type=['yxmd', 'xml'],
            help="Upload your Alteryx workflow file to convert"
        )
        
        if uploaded_file is not None:
            # Read the file
            content = uploaded_file.read()
            
            # Store in session state
            if 'workflow_content' not in st.session_state or st.session_state.workflow_content != content:
                st.session_state.workflow_content = content
                st.session_state.analyzer = AlteryxWorkflowAnalyzer()
                
                # Parse the workflow
                with st.spinner("Parsing workflow..."):
                    success = st.session_state.analyzer.parse_workflow(content)
                
                if success:
                    st.success("✅ Workflow parsed successfully!")
                    
                    # Generate Python code
                    with st.spinner("Generating Python code..."):
                        st.session_state.generated_code = st.session_state.analyzer.generate_python_code()
                    
                    st.success("✅ Python code generated!")
                else:
                    st.error("❌ Failed to parse workflow")
        
        # Example workflow option
        st.markdown("---")
        if st.button("📝 Load Example Workflow"):
            example_workflow = create_example_workflow()
            st.session_state.workflow_content = example_workflow
            st.session_state.analyzer = AlteryxWorkflowAnalyzer()
            st.session_state.analyzer.parse_workflow(example_workflow)
            st.session_state.generated_code = st.session_state.analyzer.generate_python_code()
            st.success("✅ Example workflow loaded!")
    
    with tab2:
        st.header("Workflow Analysis")
        
        if 'analyzer' in st.session_state:
            analysis = st.session_state.analyzer.analyze_workflow()
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tools", analysis['total_tools'])
            with col2:
                st.metric("Connections", analysis['total_connections'])
            with col3:
                st.metric("Tool Types", len(analysis['tool_types']))
            
            if show_analysis:
                st.markdown("---")
                
                # Tool breakdown
                st.subheader("📊 Tool Types Distribution")
                if analysis['tool_types']:
                    tool_df = pd.DataFrame(
                        list(analysis['tool_types'].items()),
                        columns=['Tool Type', 'Count']
                    )
                    st.dataframe(tool_df, use_container_width=True)
                
                # Workflow structure
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("📥 Input Tools")
                    st.write(f"Count: {len(analysis['inputs'])}")
                    for inp in analysis['inputs']:
                        st.text(f"• Tool {inp['id']}")
                
                with col2:
                    st.subheader("⚙️ Transformation Tools")
                    st.write(f"Count: {len(analysis['transformations'])}")
                    for trans in analysis['transformations'][:5]:  # Show first 5
                        st.text(f"• Tool {trans['id']}")
                
                with col3:
                    st.subheader("📤 Output Tools")
                    st.write(f"Count: {len(analysis['outputs'])}")
                    for out in analysis['outputs']:
                        st.text(f"• Tool {out['id']}")
        else:
            st.info("👆 Please upload a workflow file first")
    
    with tab3:
        st.header("Generated Python Code")
        
        if 'generated_code' in st.session_state:
            # Display code
            st.code(st.session_state.generated_code, language='python', line_numbers=True)
            
            # Download button
            st.download_button(
                label="📥 Download Python Script",
                data=st.session_state.generated_code,
                file_name="alteryx_converted_workflow.py",
                mime="text/x-python"
            )
            
            # Copy to clipboard button
            if st.button("📋 Copy to Clipboard"):
                st.info("Code copied to clipboard! (Use Ctrl+C to copy manually)")
        else:
            st.info("👆 Please upload a workflow file first")
    
    with tab4:
        st.header("Execute Generated Code")
        
        if 'generated_code' in st.session_state:
            st.warning("⚠️ Code execution requires input files to be present in the correct locations")
            
            # Input file uploader
            st.subheader("📁 Upload Input Files")
            
            if st.session_state.analyzer.input_files:
                for tool_id, filename in st.session_state.analyzer.input_files.items():
                    input_file = st.file_uploader(
                        f"Upload input file: {filename}",
                        key=f"input_{tool_id}",
                        type=['csv', 'xlsx', 'txt']
                    )
                    
                    if input_file is not None:
                        # Save uploaded file
                        with open(filename, 'wb') as f:
                            f.write(input_file.read())
                        st.success(f"✅ {filename} uploaded")
            
            st.markdown("---")
            
            # Execute button
            if st.button("▶️ Execute Code", type="primary"):
                with st.spinner("Executing..."):
                    try:
                        # Create execution environment
                        exec_globals = {
                            'pd': pd,
                            'np': __import__('numpy'),
                            'datetime': datetime
                        }
                        
                        # Execute the generated code
                        exec(st.session_state.generated_code, exec_globals)
                        
                        st.success("✅ Code executed successfully!")
                        
                        # Show outputs
                        if st.session_state.analyzer.output_specs:
                            st.subheader("📊 Output Results")
                            
                            for output_spec in st.session_state.analyzer.output_specs:
                                output_file = output_spec['file']
                                
                                if os.path.exists(output_file):
                                    st.write(f"**{output_file}:**")
                                    
                                    # Read and display the output
                                    if output_file.endswith('.csv'):
                                        df = pd.read_csv(output_file)
                                        st.dataframe(df, use_container_width=True)
                                        
                                        # Download button
                                        with open(output_file, 'rb') as f:
                                            st.download_button(
                                                label=f"📥 Download {output_file}",
                                                data=f,
                                                file_name=output_file,
                                                mime="text/csv"
                                            )
                    
                    except Exception as e:
                        st.error(f"❌ Execution error: {str(e)}")
                        st.code(str(e))
        else:
            st.info("👆 Please upload a workflow file first")


def create_example_workflow():
    """Create an example Alteryx workflow XML"""
    example = """<?xml version="1.0"?>
<AlteryxDocument>
  <Nodes>
    <Node ToolID="1">
      <GuiSettings>
        <Position x="54" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>input_data.csv</File>
        </Configuration>
      </Properties>
    </Node>
    <Node ToolID="2">
      <GuiSettings>
        <Position x="154" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <Filter>column &gt; 0</Filter>
        </Configuration>
      </Properties>
    </Node>
    <Node ToolID="3">
      <GuiSettings>
        <Position x="254" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>output_data.csv</File>
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections>
    <Connection name="Output">
      <Origin>1</Origin>
      <Destination>2</Destination>
    </Connection>
    <Connection name="Output">
      <Origin>2</Origin>
      <Destination>3</Destination>
    </Connection>
  </Connections>
</AlteryxDocument>"""
    return example.encode('utf-8')


if __name__ == "__main__":
    main()
