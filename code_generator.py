from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class PythonCodeGenerator:
    """Generate Python code from parsed Alteryx workflows"""
    
    def __init__(self, parser):
        self.parser = parser
        self.var_counter = 0
        self.tool_vars: Dict[str, str] = {}
        self.imports = set(['pandas as pd', 'numpy as np'])
        
    def generate(self) -> str:
        """Generate complete Python script"""
        code_lines = []
        
        # Header
        code_lines.extend(self._generate_header())
        code_lines.append("")
        
        # Main function
        code_lines.append("def main():")
        code_lines.append("    \"\"\"Main workflow execution function\"\"\"")
        code_lines.append("    ")
        
        # Generate code for each tool in execution order
        execution_order = self.parser.get_execution_order()
        
        for tool_id in execution_order:
            tool = self.parser.get_tool_by_id(tool_id)
            if tool:
                tool_code = self._generate_tool_code(tool)
                if tool_code:
                    # Indent all lines
                    indented_code = ['    ' + line for line in tool_code]
                    code_lines.extend(indented_code)
                    code_lines.append("    ")
        
        # Return statement
        code_lines.append("    return True")
        code_lines.append("")
        code_lines.append("")
        code_lines.append("if __name__ == '__main__':")
        code_lines.append("    main()")
        
        return "\n".join(code_lines)
    
    def _generate_header(self) -> List[str]:
        """Generate script header with imports"""
        lines = [
            "\"\"\"",
            "Auto-generated Python script from Alteryx workflow",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\"\"\"",
            ""
        ]
        
        # Add imports
        for imp in sorted(self.imports):
            lines.append(f"import {imp}")
        
        return lines
    
    def _generate_tool_code(self, tool: Dict[str, Any]) -> List[str]:
        """Generate code for a specific tool"""
        tool_type = tool['type']
        tool_id = tool['id']
        
        # Get variable name for this tool
        var_name = self._get_var_name(tool_id)
        
        # Generate comment
        annotation = tool['annotation'] or f"Tool {tool_id}"
        code = [
            f"# {'-' * 60}",
            f"# {annotation} (Type: {tool_type}, ID: {tool_id})",
            f"# {'-' * 60}"
        ]
        
        # Generate tool-specific code
        if tool_type == 'input_data':
            code.extend(self._generate_input_data(tool, var_name))
        elif tool_type == 'output_data':
            code.extend(self._generate_output_data(tool, var_name))
        elif tool_type == 'filter':
            code.extend(self._generate_filter(tool, var_name))
        elif tool_type == 'select':
            code.extend(self._generate_select(tool, var_name))
        elif tool_type == 'formula':
            code.extend(self._generate_formula(tool, var_name))
        elif tool_type == 'join':
            code.extend(self._generate_join(tool, var_name))
        elif tool_type == 'union':
            code.extend(self._generate_union(tool, var_name))
        elif tool_type == 'sort':
            code.extend(self._generate_sort(tool, var_name))
        elif tool_type == 'summarize':
            code.extend(self._generate_summarize(tool, var_name))
        elif tool_type == 'unique':
            code.extend(self._generate_unique(tool, var_name))
        elif tool_type == 'sample':
            code.extend(self._generate_sample(tool, var_name))
        elif tool_type == 'record_id':
            code.extend(self._generate_record_id(tool, var_name))
        elif tool_type == 'text_to_columns':
            code.extend(self._generate_text_to_columns(tool, var_name))
        elif tool_type == 'cross_tab':
            code.extend(self._generate_cross_tab(tool, var_name))
        elif tool_type == 'transpose':
            code.extend(self._generate_transpose(tool, var_name))
        elif tool_type == 'browse':
            code.extend(self._generate_browse(tool, var_name))
        else:
            code.extend(self._generate_generic(tool, var_name))
        
        return code
    
    def _get_var_name(self, tool_id: str) -> str:
        """Get or create variable name for tool"""
        if tool_id not in self.tool_vars:
            self.tool_vars[tool_id] = f"df_{tool_id}"
        return self.tool_vars[tool_id]
    
    def _get_source_var(self, tool_id: str) -> Optional[str]:
        """Get variable name of source tool"""
        sources = self.parser.get_source_tools(tool_id)
        if sources:
            return self._get_var_name(sources[0])
        return None
    
    def _get_all_source_vars(self, tool_id: str) -> List[str]:
        """Get variable names of all source tools"""
        sources = self.parser.get_source_tools(tool_id)
        return [self._get_var_name(src) for src in sources]
    
    # Tool-specific code generators
    
    def _generate_input_data(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Input Data tool"""
        config = tool['config']
        
        # Extract file path
        file_path = config.get('File', config.get('FileName', 'input.csv'))
        
        code = [f"# Read input file: {file_path}"]
        
        # Determine file type and read accordingly
        if file_path.endswith('.csv'):
            code.append(f"{var_name} = pd.read_csv('{file_path}')")
        elif file_path.endswith(('.xlsx', '.xls')):
            self.imports.add('openpyxl')
            code.append(f"{var_name} = pd.read_excel('{file_path}')")
        elif file_path.endswith('.txt'):
            delimiter = config.get('Delimeter', '\\t')
            code.append(f"{var_name} = pd.read_csv('{file_path}', delimiter='{delimiter}')")
        else:
            code.append(f"{var_name} = pd.read_csv('{file_path}')  # Adjust read method as needed")
        
        code.append(f"print(f'Loaded {{len({var_name})}} rows from {file_path}')")
        
        return code
    
    def _generate_output_data(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Output Data tool"""
        config = tool['config']
        source_var = self._get_source_var(tool['id'])
        
        if not source_var:
            return [f"# Output tool {tool['id']}: No source data"]
        
        # Extract output file path
        file_path = config.get('File', config.get('FileName_Out', 'output.csv'))
        
        code = [f"# Write output file: {file_path}"]
        
        # Determine file type
        if file_path.endswith('.csv'):
            code.append(f"{source_var}.to_csv('{file_path}', index=False)")
        elif file_path.endswith(('.xlsx', '.xls')):
            code.append(f"{source_var}.to_excel('{file_path}', index=False)")
        else:
            code.append(f"{source_var}.to_csv('{file_path}', index=False)")
        
        code.append(f"print(f'Wrote {{len({source_var})}} rows to {file_path}')")
        
        return code
    
    def _generate_filter(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Filter tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Filter tool: No source data"]
        
        config = tool['config']
        filter_expr = config.get('Expression', config.get('Filter', ''))
        
        code = [f"# Apply filter"]
        
        if filter_expr:
            # Try to convert Alteryx expression to pandas
            pandas_expr = self._convert_expression_to_pandas(filter_expr, source_var)
            code.append(f"{var_name} = {source_var}[{pandas_expr}]")
        else:
            code.append(f"# TODO: Add filter condition")
            code.append(f"{var_name} = {source_var}.copy()")
        
        code.append(f"print(f'Filter: {{len({var_name})}} rows (from {{len({source_var})}})')")
        
        return code
    
    def _generate_select(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Select tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Select tool: No source data"]
        
        config = tool['config']
        
        code = [f"# Select and configure fields"]
        code.append(f"{var_name} = {source_var}.copy()")
        
        # Extract field configurations if available
        # This would require parsing the SelectFields configuration
        code.append(f"# TODO: Apply field selections and type conversions")
        
        return code
    
    def _generate_formula(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Formula tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Formula tool: No source data"]
        
        config = tool['config']
        
        code = [
            f"# Apply formula",
            f"{var_name} = {source_var}.copy()"
        ]
        
        # Extract formula expression
        formula = config.get('Expression', config.get('Formula', ''))
        output_field = config.get('Field', config.get('OutputField', 'new_column'))
        
        if formula:
            pandas_expr = self._convert_expression_to_pandas(formula, var_name)
            code.append(f"{var_name}['{output_field}'] = {pandas_expr}")
        else:
            code.append(f"# TODO: Add formula expression")
            code.append(f"{var_name}['{output_field}'] = None")
        
        return code
    
    def _generate_join(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Join tool"""
        source_vars = self._get_all_source_vars(tool['id'])
        
        if len(source_vars) < 2:
            return [f"# Join tool: Insufficient source data"]
        
        left_var = source_vars[0]
        right_var = source_vars[1]
        
        config = tool['config']
        
        code = [f"# Join two datasets"]
        
        # Extract join configuration
        join_type = config.get('JoinType', 'inner').lower()
        
        # TODO: Parse join keys from config
        code.append(f"# TODO: Specify join keys")
        code.append(f"{var_name} = pd.merge(")
        code.append(f"    {left_var},")
        code.append(f"    {right_var},")
        code.append(f"    on='key_column',  # Specify join column(s)")
        code.append(f"    how='{join_type}'")
        code.append(f")")
        code.append(f"print(f'Join: {{len({var_name})}} rows')")
        
        return code
    
    def _generate_union(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Union tool"""
        source_vars = self._get_all_source_vars(tool['id'])
        
        if not source_vars:
            return [f"# Union tool: No source data"]
        
        code = [f"# Union multiple datasets"]
        
        if len(source_vars) == 1:
            code.append(f"{var_name} = {source_vars[0]}.copy()")
        else:
            union_list = ", ".join(source_vars)
            code.append(f"{var_name} = pd.concat([{union_list}], ignore_index=True)")
        
        code.append(f"print(f'Union: {{len({var_name})}} rows')")
        
        return code
    
    def _generate_sort(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Sort tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Sort tool: No source data"]
        
        config = tool['config']
        
        code = [f"# Sort data"]
        code.append(f"# TODO: Specify sort columns and order")
        code.append(f"{var_name} = {source_var}.sort_values('column_name', ascending=True)")
        
        return code
    
    def _generate_summarize(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Summarize tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Summarize tool: No source data"]
        
        code = [
            f"# Summarize/Group by",
            f"# TODO: Specify group by columns and aggregations",
            f"{var_name} = {source_var}.groupby('group_column').agg({{",
            f"    'value_column': 'sum',",
            f"    'count_column': 'count'",
            f"}}).reset_index()"
        ]
        
        return code
    
    def _generate_unique(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Unique tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Unique tool: No source data"]
        
        code = [
            f"# Remove duplicates",
            f"{var_name} = {source_var}.drop_duplicates()",
            f"print(f'Unique: {{len({var_name})}} rows (from {{len({source_var})}})')"
        ]
        
        return code
    
    def _generate_sample(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Sample tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Sample tool: No source data"]
        
        config = tool['config']
        sample_size = config.get('N', '100')
        
        code = [
            f"# Sample records",
            f"{var_name} = {source_var}.sample(n={sample_size}, random_state=42)"
        ]
        
        return code
    
    def _generate_record_id(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Record ID tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Record ID tool: No source data"]
        
        code = [
            f"# Add record ID",
            f"{var_name} = {source_var}.copy()",
            f"{var_name}['RecordID'] = range(1, len({var_name}) + 1)"
        ]
        
        return code
    
    def _generate_text_to_columns(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Text to Columns tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Text to Columns tool: No source data"]
        
        config = tool['config']
        delimiter = config.get('Delimiter', ',')
        
        code = [
            f"# Split text column",
            f"{var_name} = {source_var}.copy()",
            f"# TODO: Specify column to split",
            f"split_cols = {var_name}['text_column'].str.split('{delimiter}', expand=True)",
            f"{var_name} = pd.concat([{var_name}, split_cols], axis=1)"
        ]
        
        return code
    
    def _generate_cross_tab(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Cross Tab tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Cross Tab tool: No source data"]
        
        code = [
            f"# Create cross-tabulation",
            f"# TODO: Specify row, column, and value fields",
            f"{var_name} = pd.pivot_table(",
            f"    {source_var},",
            f"    values='value_column',",
            f"    index='row_column',",
            f"    columns='column_column',",
            f"    aggfunc='sum'",
            f").reset_index()"
        ]
        
        return code
    
    def _generate_transpose(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Transpose tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Transpose tool: No source data"]
        
        code = [
            f"# Transpose data",
            f"{var_name} = {source_var}.transpose()"
        ]
        
        return code
    
    def _generate_browse(self, tool: Dict, var_name: str) -> List[str]:
        """Generate code for Browse tool"""
        source_var = self._get_source_var(tool['id'])
        if not source_var:
            return [f"# Browse tool: No source data"]
        
        code = [
            f"# Display data (Browse equivalent)",
            f"print(f'\\nBrowse - First 10 rows:')",
            f"print({source_var}.head(10))",
            f"print(f'\\nShape: {{{source_var}.shape}}')"
        ]
        
        return code
    
    def _generate_generic(self, tool: Dict, var_name: str) -> List[str]:
        """Generate generic code for unknown tools"""
        source_var = self._get_source_var(tool['id'])
        
        code = [
            f"# Tool type '{tool['type']}' - requires manual implementation",
        ]
        
        if source_var:
            code.append(f"{var_name} = {source_var}.copy()")
            code.append(f"# TODO: Implement {tool['type']} logic")
        else:
            code.append(f"# No source data available")
        
        return code
    
    def _convert_expression_to_pandas(self, expr: str, var_name: str) -> str:
        """Convert Alteryx expression to pandas expression"""
        # This is a simplified converter - would need comprehensive mapping
        pandas_expr = expr
        
        # Replace field references: [FieldName] -> df['FieldName']
        pandas_expr = re.sub(r'\[([^\]]+)\]', f"{var_name}['\\1']", pandas_expr)
        
        # Replace common Alteryx functions
        replacements = {
            'TONUMBER': 'pd.to_numeric',
            'TOSTRING': 'str',
            'DATETIMENOW': 'pd.Timestamp.now',
            'DATETIMEPARSE': 'pd.to_datetime',
            'SUBSTRING': 'str.slice',
            'LENGTH': 'str.len',
            'TRIM': 'str.strip',
            'UPPER': 'str.upper',
            'LOWER': 'str.lower',
            'CONTAINS': 'str.contains',
            'ISNULL': 'isna',
            'IF': 'np.where',
            'AND': '&',
            'OR': '|',
            'NOT': '~'
        }
        
        for alteryx_func, pandas_func in replacements.items():
            pandas_expr = pandas_expr.replace(alteryx_func, pandas_func)
        
        return pandas_expr
