#!/usr/bin/env python3
"""
Demo script showing how to use the Alteryx converter programmatically
"""

import pandas as pd
from advanced_parser import AdvancedAlteryxParser
from code_generator import PythonCodeGenerator

def demo_basic_conversion():
    """Demonstrate basic workflow conversion"""
    print("=" * 60)
    print("DEMO: Basic Alteryx to Python Conversion")
    print("=" * 60)
    print()
    
    # Sample workflow XML
    sample_workflow = """<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2023.1">
  <Nodes>
    <Node ToolID="1">
      <GuiSettings><Position x="54" y="54" /></GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>input.csv</File>
        </Configuration>
        <Annotation><n>Read Input Data</n></Annotation>
      </Properties>
    </Node>
    
    <Node ToolID="2">
      <GuiSettings><Position x="154" y="54" /></GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <Expression>[Amount] &gt; 100</Expression>
        </Configuration>
        <Annotation><n>Filter Records</n></Annotation>
      </Properties>
    </Node>
    
    <Node ToolID="3">
      <GuiSettings><Position x="254" y="54" /></GuiSettings>
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <File>output.csv</File>
        </Configuration>
        <Annotation><n>Write Output</n></Annotation>
      </Properties>
    </Node>
  </Nodes>
  
  <Connections>
    <Connection><Origin>1</Origin><Destination>2</Destination></Connection>
    <Connection><Origin>2</Origin><Destination>3</Destination></Connection>
  </Connections>
</AlteryxDocument>"""
    
    # Step 1: Parse the workflow
    print("Step 1: Parsing workflow...")
    parser = AdvancedAlteryxParser()
    success = parser.parse(sample_workflow.encode('utf-8'))
    
    if not success:
        print("❌ Failed to parse workflow")
        return
    
    print(f"✅ Parsed successfully!")
    print(f"   - Found {len(parser.tools)} tools")
    print(f"   - Found {len(parser.connections)} connections")
    print()
    
    # Step 2: Analyze the workflow
    print("Step 2: Analyzing workflow structure...")
    execution_order = parser.get_execution_order()
    print(f"   Execution order: {' → '.join(execution_order)}")
    print()
    
    # Step 3: Generate Python code
    print("Step 3: Generating Python code...")
    generator = PythonCodeGenerator(parser)
    python_code = generator.generate()
    
    print("✅ Code generated!")
    print()
    
    # Step 4: Display the generated code
    print("Step 4: Generated Python Code:")
    print("-" * 60)
    print(python_code)
    print("-" * 60)
    print()
    
    # Step 5: Save the code
    output_file = "demo_converted_workflow.py"
    with open(output_file, 'w') as f:
        f.write(python_code)
    
    print(f"✅ Code saved to: {output_file}")
    print()

def demo_with_sample_data():
    """Demonstrate conversion with actual data execution"""
    print("=" * 60)
    print("DEMO: Conversion with Data Execution")
    print("=" * 60)
    print()
    
    # Create sample data
    print("Creating sample input data...")
    df = pd.DataFrame({
        'ID': range(1, 11),
        'Amount': [50, 150, 200, 75, 300, 125, 400, 90, 250, 180],
        'Category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
    })
    
    df.to_csv('input.csv', index=False)
    print(f"✅ Created input.csv with {len(df)} records")
    print()
    print("Sample data:")
    print(df.head())
    print()
    
    # Create workflow that processes this data
    workflow = """<?xml version="1.0"?>
<AlteryxDocument>
  <Nodes>
    <Node ToolID="1">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><File>input.csv</File></Configuration>
        <Annotation><n>Input</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="2">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><Expression>[Amount] &gt; 100</Expression></Configuration>
        <Annotation><n>Filter Amount > 100</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="3">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration></Configuration>
        <Annotation><n>Sort Descending</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="4">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><File>output.csv</File></Configuration>
        <Annotation><n>Output</n></Annotation>
      </Properties>
    </Node>
  </Nodes>
  <Connections>
    <Connection><Origin>1</Origin><Destination>2</Destination></Connection>
    <Connection><Origin>2</Origin><Destination>3</Destination></Connection>
    <Connection><Origin>3</Origin><Destination>4</Destination></Connection>
  </Connections>
</AlteryxDocument>"""
    
    # Parse and generate
    print("Parsing workflow and generating code...")
    parser = AdvancedAlteryxParser()
    parser.parse(workflow.encode('utf-8'))
    
    generator = PythonCodeGenerator(parser)
    code = generator.generate()
    
    # Save the code
    with open('demo_workflow_execution.py', 'w') as f:
        f.write(code)
    
    print("✅ Generated code saved to: demo_workflow_execution.py")
    print()
    
    # Execute the generated code
    print("Executing generated code...")
    try:
        exec_globals = {
            'pd': pd,
            'np': __import__('numpy'),
            'datetime': __import__('datetime').datetime
        }
        exec(code, exec_globals)
        
        # Read and display the output
        if pd.io.common.file_exists('output.csv'):
            output_df = pd.read_csv('output.csv')
            print("✅ Execution successful!")
            print()
            print("Output data:")
            print(output_df)
            print()
            print(f"Records in: {len(df)}, Records out: {len(output_df)}")
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
    
    print()

def demo_tool_analysis():
    """Demonstrate detailed tool analysis"""
    print("=" * 60)
    print("DEMO: Detailed Tool Analysis")
    print("=" * 60)
    print()
    
    # Complex workflow with multiple tool types
    workflow = """<?xml version="1.0"?>
<AlteryxDocument>
  <Nodes>
    <Node ToolID="1">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><File>sales.csv</File></Configuration>
        <Annotation><n>Sales Input</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="2">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><File>customers.csv</File></Configuration>
        <Annotation><n>Customer Input</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="3">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><JoinType>Inner</JoinType></Configuration>
        <Annotation><n>Join Sales and Customers</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="4">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration>
          <Field>TotalValue</Field>
          <Expression>[Quantity] * [Price]</Expression>
        </Configuration>
        <Annotation><n>Calculate Total</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="5">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration></Configuration>
        <Annotation><n>Group by Customer</n></Annotation>
      </Properties>
    </Node>
    <Node ToolID="6">
      <EngineSettings EngineDll="AlteryxBasePluginsEngine.dll" />
      <Properties>
        <Configuration><File>customer_summary.csv</File></Configuration>
        <Annotation><n>Final Output</n></Annotation>
      </Properties>
    </Node>
  </Nodes>
  <Connections>
    <Connection><Origin>1</Origin><Destination>3</Destination></Connection>
    <Connection><Origin>2</Origin><Destination>3</Destination></Connection>
    <Connection><Origin>3</Origin><Destination>4</Destination></Connection>
    <Connection><Origin>4</Origin><Destination>5</Destination></Connection>
    <Connection><Origin>5</Origin><Destination>6</Destination></Connection>
  </Connections>
</AlteryxDocument>"""
    
    # Parse
    parser = AdvancedAlteryxParser()
    parser.parse(workflow.encode('utf-8'))
    
    print(f"Total tools: {len(parser.tools)}")
    print(f"Total connections: {len(parser.connections)}")
    print()
    
    # Analyze each tool
    print("Tool Details:")
    print("-" * 60)
    for tool in parser.tools:
        print(f"\nTool ID: {tool['id']}")
        print(f"  Type: {tool['type']}")
        print(f"  Annotation: {tool['annotation'] or 'None'}")
        
        # Show connections
        sources = parser.get_source_tools(tool['id'])
        destinations = parser.get_destination_tools(tool['id'])
        
        if sources:
            print(f"  Input from: {', '.join(sources)}")
        if destinations:
            print(f"  Output to: {', '.join(destinations)}")
    
    print()
    print("-" * 60)
    
    # Show execution order
    print("\nExecution Order:")
    execution_order = parser.get_execution_order()
    for idx, tool_id in enumerate(execution_order, 1):
        tool = parser.get_tool_by_id(tool_id)
        print(f"  {idx}. Tool {tool_id} - {tool['annotation'] or tool['type']}")
    
    print()

def main():
    """Run all demos"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Alteryx to Python Converter - Demo" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    demos = [
        ("Basic Conversion", demo_basic_conversion),
        ("Conversion with Data", demo_with_sample_data),
        ("Tool Analysis", demo_tool_analysis)
    ]
    
    for idx, (name, func) in enumerate(demos, 1):
        print(f"\n{'=' * 60}")
        print(f"Running Demo {idx}/{len(demos)}: {name}")
        print('=' * 60)
        input("\nPress Enter to continue...")
        print()
        
        try:
            func()
        except Exception as e:
            print(f"❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        
        if idx < len(demos):
            print("\n" + "=" * 60)
            print(f"Demo {idx} complete!")
            print("=" * 60)
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - demo_converted_workflow.py")
    print("  - demo_workflow_execution.py")
    print("  - input.csv")
    print("  - output.csv (if execution succeeded)")
    print("\nTo run the web app, use: streamlit run app.py")
    print()

if __name__ == "__main__":
    main()
