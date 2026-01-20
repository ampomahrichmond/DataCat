import streamlit as st
import pandas as pd
import io
import os
import traceback
from pathlib import Path
from datetime import datetime
from advanced_parser import AdvancedAlteryxParser
from code_generator import PythonCodeGenerator

# Page configuration
st.set_page_config(
    page_title="Alteryx to Python Converter Pro",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .code-block {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'parser' not in st.session_state:
        st.session_state.parser = None
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'workflow_uploaded' not in st.session_state:
        st.session_state.workflow_uploaded = False
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = {}
    if 'input_files' not in st.session_state:
        st.session_state.input_files = {}

def create_sample_workflow():
    """Create a sample Alteryx workflow for testing"""
    sample_xml = """<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2023.1">
  <Nodes>
    <!-- Input Data Tool -->
    <Node ToolID="1">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="54" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>sales_data.csv</File>
          <FormatSpecificOptions>
            <HeaderRow>True</HeaderRow>
            <IgnoreErrors>False</IgnoreErrors>
            <AllowShareWrite>False</AllowShareWrite>
            <TempFile>False</TempFile>
            <FirstRowData>False</FirstRowData>
          </FormatSpecificOptions>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Sales Data Input</Name>
          <DefaultAnnotationText>sales_data.csv</DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
    
    <!-- Filter Tool -->
    <Node ToolID="2">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="154" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <Expression>[Amount] &gt; 1000</Expression>
          <Mode>Custom</Mode>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Filter Large Sales</Name>
          <DefaultAnnotationText>[Amount] &gt; 1000</DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
    
    <!-- Formula Tool -->
    <Node ToolID="3">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="254" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <Field>Commission</Field>
          <Expression>[Amount] * 0.10</Expression>
          <Type>Double</Type>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Calculate Commission</Name>
          <DefaultAnnotationText>Commission = [Amount] * 0.10</DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
    
    <!-- Summarize Tool -->
    <Node ToolID="4">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="354" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <GroupBy>
            <Field field="Region" />
          </GroupBy>
          <Summarize>
            <Field field="Amount" action="Sum" />
            <Field field="Amount" action="Count" />
          </Summarize>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Summarize by Region</Name>
          <DefaultAnnotationText></DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
    
    <!-- Sort Tool -->
    <Node ToolID="5">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="454" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <OrderFields>
            <Field field="Sum_Amount" order="Desc" />
          </OrderFields>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Sort by Total</Name>
          <DefaultAnnotationText>Sum_Amount - Desc</DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
    
    <!-- Output Data Tool -->
    <Node ToolID="6">
      <GuiSettings Plugin="AlteryxBasePluginsGui.dll">
        <Position x="554" y="54" />
      </GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>regional_summary.csv</File>
        </Configuration>
        <Annotation DisplayMode="0">
          <Name>Regional Summary Output</Name>
          <DefaultAnnotationText>regional_summary.csv</DefaultAnnotationText>
        </Annotation>
      </Properties>
    </Node>
  </Nodes>
  
  <Connections>
    <Connection>
      <Origin ToolID="1" Connection="Output" />
      <Destination ToolID="2" Connection="Input" />
    </Connection>
    <Connection>
      <Origin ToolID="2" Connection="Output" />
      <Destination ToolID="3" Connection="Input" />
    </Connection>
    <Connection>
      <Origin ToolID="3" Connection="Output" />
      <Destination ToolID="4" Connection="Input" />
    </Connection>
    <Connection>
      <Origin ToolID="4" Connection="Output" />
      <Destination ToolID="5" Connection="Input" />
    </Connection>
    <Connection>
      <Origin ToolID="5" Connection="Output" />
      <Destination ToolID="6" Connection="Input" />
    </Connection>
  </Connections>
</AlteryxDocument>"""
    return sample_xml.encode('utf-8')

def create_sample_data():
    """Create sample CSV data for testing"""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    n_records = 100
    
    df = pd.DataFrame({
        'OrderID': range(1, n_records + 1),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'Amount': np.random.uniform(500, 5000, n_records).round(2),
        'Product': np.random.choice(['Product A', 'Product B', 'Product C'], n_records),
        'Date': pd.date_range('2024-01-01', periods=n_records, freq='D')
    })
    
    return df

def sidebar_info():
    """Render sidebar information"""
    with st.sidebar:
        st.image("https://via.placeholder.com/250x100/1f77b4/ffffff?text=Alteryx+to+Python", use_container_width=True)
        
        st.markdown("---")
        st.header("📚 Quick Guide")
        
        with st.expander("🔹 Supported Tools"):
            st.markdown("""
            - **Input/Output**: Input Data, Output Data, Text Input
            - **Preparation**: Select, Filter, Formula, Sample, Record ID
            - **Join**: Join, Union, Find Replace
            - **Transform**: Summarize, Sort, Unique, Cross Tab, Transpose
            - **Parse**: Text to Columns, RegEx, DateTime
            - **Documentation**: Browse, Comment
            """)
        
        with st.expander("🔹 How to Use"):
            st.markdown("""
            1. **Upload** your Alteryx workflow (.yxmd)
            2. **Review** the analysis and generated code
            3. **Upload** any required input files
            4. **Execute** the Python code
            5. **Download** your results
            """)
        
        with st.expander("🔹 Features"):
            st.markdown("""
            - ✅ Automatic code generation
            - ✅ Workflow visualization
            - ✅ Interactive execution
            - ✅ File handling
            - ✅ Error detection
            - ✅ Code download
            """)
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        st.session_state.auto_execute = st.checkbox("Auto-execute after upload", value=False)
        st.session_state.show_warnings = st.checkbox("Show warnings", value=True)
        st.session_state.verbose_output = st.checkbox("Verbose output", value=True)
        
        st.markdown("---")
        st.info("💡 **Tip**: Start with the sample workflow to see how it works!")

def main():
    initialize_session_state()
    sidebar_info()
    
    # Header
    st.markdown('<div class="main-header">🔄 Alteryx to Python Converter Pro</div>', unsafe_allow_html=True)
    st.markdown("Transform your Alteryx workflows into production-ready Python scripts")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📁 Upload", 
        "🔍 Analysis", 
        "💻 Generated Code", 
        "📂 Input Files",
        "▶️ Execute"
    ])
    
    # Tab 1: Upload Workflow
    with tab1:
        st.header("Upload Alteryx Workflow")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose your Alteryx workflow file (.yxmd or .xml)",
                type=['yxmd', 'xml', 'yxmc'],
                help="Upload an Alteryx workflow to convert to Python"
            )
            
            if uploaded_file is not None:
                try:
                    content = uploaded_file.read()
                    
                    with st.spinner("🔄 Parsing workflow..."):
                        parser = AdvancedAlteryxParser()
                        success = parser.parse(content)
                        
                        if success:
                            st.session_state.parser = parser
                            st.session_state.workflow_uploaded = True
                            
                            # Generate code
                            with st.spinner("🔄 Generating Python code..."):
                                generator = PythonCodeGenerator(parser)
                                st.session_state.generated_code = generator.generate()
                            
                            st.success("✅ Workflow parsed and code generated successfully!")
                            
                            # Show quick stats
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Tools Found", len(parser.tools))
                            with col_b:
                                st.metric("Connections", len(parser.connections))
                            with col_c:
                                execution_order = parser.get_execution_order()
                                st.metric("Execution Steps", len(execution_order))
                        else:
                            st.error("❌ Failed to parse workflow. Please check the file format.")
                            
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    if st.session_state.show_warnings:
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())
        
        with col2:
            st.subheader("📝 Try Sample")
            st.write("No workflow? Try our sample!")
            
            if st.button("🚀 Load Sample Workflow", use_container_width=True):
                sample_workflow = create_sample_workflow()
                
                parser = AdvancedAlteryxParser()
                parser.parse(sample_workflow)
                st.session_state.parser = parser
                st.session_state.workflow_uploaded = True
                
                generator = PythonCodeGenerator(parser)
                st.session_state.generated_code = generator.generate()
                
                # Create sample data
                sample_df = create_sample_data()
                sample_df.to_csv('sales_data.csv', index=False)
                st.session_state.input_files['sales_data.csv'] = sample_df
                
                st.success("✅ Sample workflow loaded!")
                st.rerun()
    
    # Tab 2: Analysis
    with tab2:
        st.header("Workflow Analysis")
        
        if st.session_state.workflow_uploaded and st.session_state.parser:
            parser = st.session_state.parser
            
            # Metadata
            st.subheader("📊 Workflow Metadata")
            metadata_col1, metadata_col2 = st.columns(2)
            
            with metadata_col1:
                st.write(f"**Version:** {parser.metadata.get('version', 'Unknown')}")
                st.write(f"**Tools:** {len(parser.tools)}")
            
            with metadata_col2:
                st.write(f"**Connections:** {len(parser.connections)}")
                execution_order = parser.get_execution_order()
                st.write(f"**Execution Steps:** {len(execution_order)}")
            
            st.markdown("---")
            
            # Tool breakdown
            st.subheader("🔧 Tools Breakdown")
            
            tool_types = {}
            for tool in parser.tools:
                tool_type = tool['type']
                tool_types[tool_type] = tool_types.get(tool_type, 0) + 1
            
            if tool_types:
                tool_df = pd.DataFrame([
                    {'Tool Type': k, 'Count': v} 
                    for k, v in sorted(tool_types.items(), key=lambda x: x[1], reverse=True)
                ])
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.dataframe(tool_df, use_container_width=True, hide_index=True)
                
                with col2:
                    import plotly.express as px
                    fig = px.pie(tool_df, values='Count', names='Tool Type', title='Tool Distribution')
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Execution flow
            st.subheader("🔄 Execution Flow")
            
            execution_order = parser.get_execution_order()
            
            flow_data = []
            for idx, tool_id in enumerate(execution_order, 1):
                tool = parser.get_tool_by_id(tool_id)
                if tool:
                    flow_data.append({
                        'Step': idx,
                        'Tool ID': tool_id,
                        'Type': tool['type'],
                        'Annotation': tool['annotation'] or '-'
                    })
            
            if flow_data:
                flow_df = pd.DataFrame(flow_data)
                st.dataframe(flow_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Detailed tool information
            st.subheader("📋 Detailed Tool Information")
            
            for tool in parser.tools:
                with st.expander(f"Tool {tool['id']}: {tool['type']} - {tool['annotation'] or 'No annotation'}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Info:**")
                        st.json({
                            'ID': tool['id'],
                            'Type': tool['type'],
                            'Plugin': tool['plugin']
                        })
                    
                    with col2:
                        st.write("**Position:**")
                        st.json(tool['gui'])
                    
                    if tool['config']:
                        st.write("**Configuration:**")
                        st.json(tool['config'])
                    
                    # Show connections
                    sources = parser.get_source_tools(tool['id'])
                    destinations = parser.get_destination_tools(tool['id'])
                    
                    if sources or destinations:
                        st.write("**Connections:**")
                        if sources:
                            st.write(f"  ⬅️ From: {', '.join(sources)}")
                        if destinations:
                            st.write(f"  ➡️ To: {', '.join(destinations)}")
        
        else:
            st.info("👆 Please upload a workflow file first")
    
    # Tab 3: Generated Code
    with tab3:
        st.header("Generated Python Code")
        
        if st.session_state.generated_code:
            st.subheader("📝 Complete Script")
            
            # Display code
            st.code(st.session_state.generated_code, language='python', line_numbers=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📥 Download Python Script",
                    data=st.session_state.generated_code,
                    file_name=f"alteryx_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                    mime="text/x-python",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📥 Download Requirements",
                    data="pandas>=2.0.0\nnumpy>=1.24.0\nopenpyxl>=3.1.0",
                    file_name="requirements.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.info("💡 Use the copy button in the code block above")
            
            # Code statistics
            st.markdown("---")
            st.subheader("📊 Code Statistics")
            
            lines = st.session_state.generated_code.split('\n')
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            comment_lines = [l for l in lines if l.strip().startswith('#')]
            blank_lines = [l for l in lines if not l.strip()]
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Lines", len(lines))
            with stat_col2:
                st.metric("Code Lines", len(code_lines))
            with stat_col3:
                st.metric("Comments", len(comment_lines))
            with stat_col4:
                st.metric("Blank Lines", len(blank_lines))
        
        else:
            st.info("👆 Please upload a workflow file first")
    
    # Tab 4: Input Files
    with tab4:
        st.header("Input Files Management")
        
        if st.session_state.workflow_uploaded and st.session_state.parser:
            st.write("Upload the input files required by your workflow:")
            
            # Find all input tools
            input_tools = [tool for tool in st.session_state.parser.tools if tool['type'] == 'input_data']
            
            if input_tools:
                for tool in input_tools:
                    config = tool['config']
                    filename = config.get('File', config.get('FileName', 'input.csv'))
                    
                    st.subheader(f"📄 {filename}")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        uploaded_input = st.file_uploader(
                            f"Upload {filename}",
                            key=f"input_{tool['id']}",
                            type=['csv', 'xlsx', 'xls', 'txt'],
                            help=f"Upload the input file for Tool {tool['id']}"
                        )
                        
                        if uploaded_input is not None:
                            try:
                                # Read and save the file
                                if filename.endswith('.csv'):
                                    df = pd.read_csv(uploaded_input)
                                elif filename.endswith(('.xlsx', '.xls')):
                                    df = pd.read_excel(uploaded_input)
                                else:
                                    df = pd.read_csv(uploaded_input)
                                
                                # Save to disk
                                df.to_csv(filename, index=False)
                                st.session_state.input_files[filename] = df
                                
                                st.success(f"✅ {filename} uploaded successfully!")
                                
                                # Preview
                                with st.expander("👁️ Preview Data"):
                                    st.dataframe(df.head(10), use_container_width=True)
                                    st.write(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                            
                            except Exception as e:
                                st.error(f"❌ Error loading file: {str(e)}")
                    
                    with col2:
                        if filename in st.session_state.input_files:
                            st.success("✅ Loaded")
                            df = st.session_state.input_files[filename]
                            st.metric("Rows", f"{len(df):,}")
                            st.metric("Columns", len(df.columns))
            else:
                st.info("ℹ️ No input tools found in workflow")
        
        else:
            st.info("👆 Please upload a workflow file first")
    
    # Tab 5: Execute
    with tab5:
        st.header("Execute Python Code")
        
        if st.session_state.generated_code:
            # Check if input files are ready
            input_tools = [tool for tool in st.session_state.parser.tools if tool['type'] == 'input_data']
            input_files_ready = all(
                tool['config'].get('File', tool['config'].get('FileName', '')) in st.session_state.input_files
                for tool in input_tools
            )
            
            if not input_files_ready and input_tools:
                st.warning("⚠️ Please upload all required input files in the 'Input Files' tab before executing")
            
            st.markdown("---")
            
            # Execution button
            if st.button("▶️ Execute Workflow", type="primary", use_container_width=True, disabled=not input_files_ready):
                with st.spinner("🔄 Executing workflow..."):
                    try:
                        # Create execution environment
                        exec_globals = {
                            'pd': pd,
                            'np': __import__('numpy'),
                            'datetime': datetime,
                            '__name__': '__main__'
                        }
                        
                        # Capture print output
                        import io
                        import sys
                        
                        old_stdout = sys.stdout
                        sys.stdout = output_capture = io.StringIO()
                        
                        try:
                            # Execute the code
                            exec(st.session_state.generated_code, exec_globals)
                            
                            # Get output
                            output = output_capture.getvalue()
                        finally:
                            sys.stdout = old_stdout
                        
                        st.success("✅ Code executed successfully!")
                        
                        # Show console output
                        if output:
                            st.subheader("📋 Console Output")
                            st.code(output, language='text')
                        
                        # Show output files
                        st.markdown("---")
                        st.subheader("📊 Output Results")
                        
                        output_tools = [tool for tool in st.session_state.parser.tools if tool['type'] == 'output_data']
                        
                        for tool in output_tools:
                            config = tool['config']
                            output_file = config.get('File', config.get('FileName_Out', 'output.csv'))
                            
                            if os.path.exists(output_file):
                                st.write(f"**{output_file}:**")
                                
                                try:
                                    if output_file.endswith('.csv'):
                                        df = pd.read_csv(output_file)
                                    elif output_file.endswith(('.xlsx', '.xls')):
                                        df = pd.read_excel(output_file)
                                    else:
                                        df = pd.read_csv(output_file)
                                    
                                    # Display
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.dataframe(df, use_container_width=True)
                                    
                                    with col2:
                                        st.metric("Rows", f"{len(df):,}")
                                        st.metric("Columns", len(df.columns))
                                        
                                        # Download button
                                        with open(output_file, 'rb') as f:
                                            st.download_button(
                                                label=f"📥 Download",
                                                data=f,
                                                file_name=output_file,
                                                mime="text/csv" if output_file.endswith('.csv') else "application/vnd.ms-excel",
                                                use_container_width=True
                                            )
                                
                                except Exception as e:
                                    st.error(f"Error reading output file: {str(e)}")
                    
                    except Exception as e:
                        st.error(f"❌ Execution error: {str(e)}")
                        
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())
        
        else:
            st.info("👆 Please upload a workflow file first")

if __name__ == "__main__":
    # Install plotly if not available
    try:
        import plotly.express as px
    except ImportError:
        st.warning("Installing plotly for visualizations...")
        os.system("pip install plotly --break-system-packages")
        st.rerun()
    
    main()
