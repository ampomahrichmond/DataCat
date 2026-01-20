# Installation & Setup Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Download Files
You should have all these files:
- ✅ app.py
- ✅ advanced_parser.py
- ✅ code_generator.py
- ✅ alteryx_converter.py
- ✅ requirements.txt
- ✅ demo.py
- ✅ run.sh (for Mac/Linux)
- ✅ run.bat (for Windows)
- ✅ README.md
- ✅ QUICKSTART.md
- ✅ PROJECT_OVERVIEW.md

### Step 2: Install Python Dependencies

**Option A: Quick Install**
```bash
pip install -r requirements.txt
```

**Option B: Manual Install**
```bash
pip install streamlit pandas numpy openpyxl plotly
```

**For Linux/WSL users (may need --break-system-packages flag):**
```bash
pip install -r requirements.txt --break-system-packages
```

### Step 3: Launch the Application

**On Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**On Windows:**
```cmd
run.bat
```

**Or use Python directly:**
```bash
streamlit run app.py
```

### Step 4: Access the Application

The application will automatically open in your browser at:
```
http://localhost:8501
```

If it doesn't open automatically, manually navigate to that URL.

## 📝 Verification

### Check Installation
```bash
# Check Python version (should be 3.8+)
python --version

# Check pip
pip --version

# Verify packages
pip list | grep streamlit
pip list | grep pandas
pip list | grep plotly
```

### Test the Application

1. Launch the app
2. Click "Load Sample Workflow"
3. Navigate through the tabs
4. Click "Execute Workflow"
5. Verify you see results

If all steps work, you're ready to go! ✅

## 🔧 Troubleshooting

### Issue: "streamlit: command not found"
**Solution:**
```bash
pip install --upgrade streamlit
# or
python -m streamlit run app.py
```

### Issue: "Module not found" errors
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Port 8501 already in use
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: Permission denied on run.sh
**Solution:**
```bash
chmod +x run.sh
./run.sh
```

## 🎯 Next Steps

1. ✅ **Try the Demo**
   ```bash
   python demo.py
   ```

2. ✅ **Upload Your Workflow**
   - Use the Upload tab
   - Select your .yxmd file
   - Review the generated code

3. ✅ **Customize**
   - Edit generated code as needed
   - Add custom logic
   - Optimize for your use case

4. ✅ **Deploy**
   - Save generated scripts
   - Use in production
   - Schedule with cron/Task Scheduler

## 📚 Documentation

- **README.md** - Complete feature documentation
- **QUICKSTART.md** - Fast-track guide
- **PROJECT_OVERVIEW.md** - Technical architecture
- **Code comments** - Inline documentation

## 🎓 Learning Path

### Beginner
1. Read QUICKSTART.md
2. Run the sample workflow
3. Try uploading a simple workflow
4. Review generated code

### Intermediate
1. Run demo.py
2. Upload complex workflows
3. Customize generated code
4. Add error handling

### Advanced
1. Study advanced_parser.py
2. Extend tool support
3. Optimize code generation
4. Contribute improvements

## ⚡ Performance Tips

### For Large Workflows
1. Generate code in UI
2. Download the Python script
3. Run locally with optimizations
4. Use chunking for big data

### For Production
1. Review generated code
2. Add robust error handling
3. Implement logging
4. Add data validation

## 🔐 Security Notes

- Input files are processed locally
- No data sent to external servers
- Generated code is pure Python
- Clean up temp files after use

## 📞 Getting Help

1. **Check Documentation**
   - README.md for features
   - QUICKSTART.md for basics
   - Code comments for details

2. **Run Demos**
   - demo.py for examples
   - Sample workflow in UI

3. **Debug**
   - Enable verbose output
   - Check console messages
   - Review error traces

## ✅ Final Checklist

Before starting your first conversion:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Application launches successfully
- [ ] Sample workflow works
- [ ] Can upload files
- [ ] Can execute workflows
- [ ] Can download results
- [ ] Documentation reviewed

**Ready to convert! 🎉**

---

For detailed information, see:
- README.md - Full documentation
- QUICKSTART.md - Quick guide
- PROJECT_OVERVIEW.md - Architecture details
