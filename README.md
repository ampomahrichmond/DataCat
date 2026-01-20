# Alteryx to Python Converter Pro 🔄

A powerful Python application that analyzes Alteryx workflows (.yxmd files) and converts them into production-ready Python scripts. Features an interactive web-based UI built with Streamlit for easy workflow management and execution.

## Features ✨

### Core Capabilities
- **Workflow Parsing**: Comprehensive XML parsing of Alteryx workflows
- **Code Generation**: Automatic Python/pandas code generation
- **Interactive UI**: User-friendly Streamlit interface
- **Workflow Analysis**: Detailed breakdown of tools and connections
- **File Management**: Upload and manage input/output files
- **Live Execution**: Execute generated code directly in the UI
- **Code Download**: Export generated Python scripts and requirements

### Supported Alteryx Tools

#### Input/Output Tools
- Input Data (CSV, Excel, TXT)
- Output Data
- Text Input
- Browse

#### Preparation Tools
- Select
- Filter
- Formula
- Multi-Field Formula
- Sample
- Record ID
- Auto Field
- Data Cleansing

#### Join Tools
- Join
- Join Multiple
- Union
- Find Replace
- Append Fields

#### Transform Tools
- Summarize
- Cross Tab
- Transpose
- Running Total
- Sort
- Unique

#### Parse Tools
- Text to Columns
- RegEx
- DateTime

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this project**
   ```bash
   cd alteryx-to-python-converter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will open automatically in your default browser at `http://localhost:8501`

## Quick Start 🎯

### Option 1: Use Sample Workflow

1. Launch the application
2. Click "Load Sample Workflow" button
3. Explore the tabs to see:
   - Generated Python code
   - Workflow analysis
   - Sample data execution

### Option 2: Upload Your Workflow

1. Click the "Upload" tab
2. Upload your Alteryx .yxmd file
3. Review the workflow analysis
4. Upload required input files
5. Execute the generated Python code
6. Download results

## Application Structure 📁

```
alteryx-to-python-converter/
├── app.py                      # Main Streamlit application
├── alteryx_converter.py        # Basic converter (standalone)
├── advanced_parser.py          # Advanced Alteryx workflow parser
├── code_generator.py           # Python code generator
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── run.sh                      # Startup script (Unix/Linux/Mac)
```

## Usage Guide 📖

### 1. Upload Workflow

Navigate to the **Upload** tab:
- Click "Choose your Alteryx workflow file"
- Select a .yxmd or .xml file
- Or click "Load Sample Workflow" to try the demo

### 2. Analyze Workflow

Navigate to the **Analysis** tab to view:
- Workflow metadata
- Tool type distribution
- Execution flow
- Detailed tool configurations
- Connection mappings

### 3. Review Generated Code

Navigate to the **Generated Code** tab:
- View the complete Python script
- Check code statistics
- Download the script
- Download requirements.txt

### 4. Upload Input Files

Navigate to the **Input Files** tab:
- Upload CSV, Excel, or TXT files
- Preview uploaded data
- Verify data dimensions

### 5. Execute Workflow

Navigate to the **Execute** tab:
- Click "Execute Workflow"
- View console output
- Examine output results
- Download generated files

## Code Generation Details 💻

### Generated Script Structure

Each generated Python script includes:

1. **Header**: Documentation and metadata
2. **Imports**: Required Python libraries
3. **Main Function**: Complete workflow logic
4. **Tool Comments**: Descriptive annotations
5. **Error Handling**: Basic exception handling
6. **Print Statements**: Progress tracking

### Example Generated Code

```python
"""
Auto-generated Python script from Alteryx workflow
Generated: 2024-01-20 10:30:00
"""

import pandas as pd
import numpy as np
from datetime import datetime

def main():
    """Main workflow execution function"""
    
    # ------------------------------------------------------------
    # Sales Data Input (Type: input_data, ID: 1)
    # ------------------------------------------------------------
    # Read input file: sales_data.csv
    df_1 = pd.read_csv('sales_data.csv')
    print(f'Loaded {len(df_1)} rows from sales_data.csv')
    
    # ------------------------------------------------------------
    # Filter Large Sales (Type: filter, ID: 2)
    # ------------------------------------------------------------
    # Apply filter
    df_2 = df_1[df_1['Amount'] > 1000]
    print(f'Filter: {len(df_2)} rows (from {len(df_1)})')
    
    # ... more transformations ...
    
    return True

if __name__ == '__main__':
    main()
```

## Configuration ⚙️

### Sidebar Settings

- **Auto-execute after upload**: Automatically run code after generation
- **Show warnings**: Display warning messages
- **Verbose output**: Show detailed execution logs

## Advanced Features 🔧

### Custom Tool Mapping

The converter can be extended to support custom Alteryx tools by modifying:
- `advanced_parser.py`: Add tool detection logic
- `code_generator.py`: Add code generation methods

### Expression Conversion

The converter includes logic to transform Alteryx expressions to pandas:
- Field references: `[FieldName]` → `df['FieldName']`
- Functions: `TONUMBER()` → `pd.to_numeric()`
- Operators: `AND` → `&`, `OR` → `|`

### Execution Order

The parser uses topological sorting to determine the correct execution order of tools based on their connections.

## Troubleshooting 🔍

### Common Issues

**Issue**: Workflow won't parse
- **Solution**: Ensure the file is a valid .yxmd XML file
- Check for XML syntax errors

**Issue**: Input files not found during execution
- **Solution**: Upload all required input files in the "Input Files" tab
- Verify file names match exactly

**Issue**: Generated code has errors
- **Solution**: Review unsupported tools marked with "TODO"
- Manually implement custom logic for complex tools

**Issue**: Streamlit won't start
- **Solution**: Ensure all dependencies are installed
- Try: `pip install --upgrade streamlit`

### Debug Mode

To enable detailed error messages:
1. Open sidebar settings
2. Enable "Show warnings"
3. Enable "Verbose output"

## Limitations ⚠️

### Current Limitations

1. **Complex Macros**: Custom macros require manual implementation
2. **Spatial Tools**: GIS/spatial tools not yet supported
3. **Predictive Tools**: Machine learning tools need manual coding
4. **Database Connections**: In-DB tools converted to file operations
5. **R/Python Tools**: Embedded scripts need manual extraction

### Workarounds

- For unsupported tools, the generator creates TODO comments
- Manual implementation required for complex transformations
- Use the generated code as a starting template

## Performance Tips 💡

1. **Large Files**: Process large datasets in chunks
2. **Memory**: Monitor memory usage for big workflows
3. **Execution**: Run complex workflows outside the UI for better performance
4. **Optimization**: Review generated code for optimization opportunities

## Contributing 🤝

To extend this tool:

1. **Add New Tool Support**:
   - Update `TOOL_MAPPINGS` in `advanced_parser.py`
   - Add generation method in `code_generator.py`

2. **Improve Expression Conversion**:
   - Enhance `_convert_expression_to_pandas()` method
   - Add more Alteryx function mappings

3. **UI Enhancements**:
   - Modify `app.py` for new features
   - Add visualization components

## Technical Details 🔬

### Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **openpyxl**: Excel file support
- **plotly**: Interactive visualizations

### Architecture

```
User Upload → XML Parser → Tool Analyzer → Code Generator → Streamlit UI → Execution Engine
```

### Parser Logic

1. Parse XML structure
2. Extract tool nodes and properties
3. Identify tool types
4. Build connection graph
5. Perform topological sort
6. Generate execution order

### Code Generator Logic

1. Process tools in execution order
2. Map tools to Python equivalents
3. Generate pandas operations
4. Add error handling
5. Include progress tracking
6. Format with comments

## Future Enhancements 🚀

Planned features:
- [ ] Support for more Alteryx tools
- [ ] Better expression parsing
- [ ] Visual workflow diagram
- [ ] Code optimization suggestions
- [ ] Unit test generation
- [ ] Performance profiling
- [ ] Export to Jupyter notebooks
- [ ] Multi-workflow conversion
- [ ] Database connector support
- [ ] Cloud deployment options

## License 📄

This is a development tool for converting Alteryx workflows to Python. 
Ensure you have appropriate licenses for both Alteryx and any data you process.

## Support 💬

For issues, questions, or contributions:
- Review the code comments for implementation details
- Check the Troubleshooting section
- Examine generated code for TODO markers
- Modify the tool mappings for custom needs

## Version History 📝

### v1.0.0 (Current)
- Initial release
- Core tool support
- Interactive UI
- File management
- Code execution

---

**Built with ❤️ for data professionals moving from Alteryx to Python**

Happy Converting! 🎉
