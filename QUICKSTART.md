# Quick Start Guide 🚀

## 3-Minute Setup

### Step 1: Install Python (if needed)
Download Python 3.8+ from [python.org](https://python.org)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch Application

**On Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**On Windows:**
```cmd
run.bat
```

**Or directly:**
```bash
streamlit run app.py
```

## First Steps in the Application

1. **Load Sample Workflow**
   - Click "📝 Load Sample Workflow" button
   - This creates a complete example workflow with sample data

2. **Explore the Tabs**
   - **Analysis**: See workflow breakdown
   - **Generated Code**: View the Python script
   - **Execute**: Run the workflow and see results

3. **Try Your Own Workflow**
   - Upload a .yxmd file in the Upload tab
   - Upload input files if required
   - Execute and download results

## Example: Sales Analysis Workflow

The sample workflow demonstrates:
- Reading CSV input
- Filtering data (Amount > 1000)
- Adding calculated fields (Commission)
- Summarizing by region
- Sorting results
- Writing output

### Expected Output
```
Regional sales summary with:
- Total sales by region
- Count of transactions
- Sorted by highest sales
```

## Common Use Cases

### 1. Simple Data Transformation
```
Input → Filter → Output
```
Perfect for: Data cleaning, subsetting

### 2. Aggregation Pipeline
```
Input → Summarize → Sort → Output
```
Perfect for: Reports, analytics

### 3. Multi-Source Join
```
Input A ↘
         Join → Filter → Output
Input B ↗
```
Perfect for: Combining datasets

### 4. Complex ETL
```
Input → Multiple transformations → Multiple outputs
```
Perfect for: Data pipelines

## Tips & Tricks

### Performance
- For large files, execute generated scripts directly (not in UI)
- Use chunking for very large datasets
- Optimize generated code for your specific needs

### Customization
- Edit generated code to add custom logic
- Use TODO comments as implementation guides
- Add error handling and validation

### Debugging
- Enable "Show warnings" in settings
- Check console output during execution
- Review tool configurations in Analysis tab

## Next Steps

1. ✅ **Try the sample** - Get familiar with the interface
2. ✅ **Upload your workflow** - Test with real data
3. ✅ **Review generated code** - Understand the conversion
4. ✅ **Customize** - Adapt code to your needs
5. ✅ **Deploy** - Use in production

## Getting Help

- Check README.md for full documentation
- Review code comments for implementation details
- Look for TODO markers in generated code
- Examine error messages in the UI

## What's Supported

✅ Input/Output tools (CSV, Excel, TXT)  
✅ Filter, Select, Formula  
✅ Join, Union  
✅ Sort, Summarize, Unique  
✅ Sample, Record ID  
✅ Text to Columns  
✅ Cross Tab, Transpose  

## What Requires Manual Work

⚠️ Complex macros  
⚠️ Spatial/GIS tools  
⚠️ Predictive tools  
⚠️ Database connections  
⚠️ R/Python embedded code  

---

**Happy Converting! 🎉**

For detailed information, see the full README.md
