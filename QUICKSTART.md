# Quick Start Guide

Get started in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd crime_report_extractor
pip install -r requirements.txt
```

## Step 2: Get DeepSeek API Key (2 minutes)

1. Go to [https://www.deepseek.com](https://www.deepseek.com)
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key
5. Copy the key

## Step 3: Set API Key (30 seconds)

**Mac/Linux:**
```bash
export DEEPSEEK_API_KEY="your-key-here"
```

**Windows (Command Prompt):**
```cmd
set DEEPSEEK_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY="your-key-here"
```

**Or edit config.py directly:**
```python
DEEPSEEK_API_KEY = 'your-key-here'
```

## Step 4: Prepare Your Data (1 minute)

Put your Excel file in the `input/` folder with this format:

| crime_code | narrative |
|------------|-----------|
| 220 | Officers responded to... |
| 510 | Victim reported... |

Name it: `crime_data.xlsx`

**Or** use the included sample file to test first!

## Step 5: Run It! (30 seconds)

```bash
python main.py
```

That's it! Results will be in `output/crime_data_extracted.xlsx`

---

## Without API Key (Free Mode)

Don't want to use the API? No problem:

```bash
python main.py
```

The script will automatically use regex-only extraction:
- ✅ Still works
- ✅ Completely free
- ⚠️ Lower accuracy (60-75% vs 85-95%)
- ⚠️ May miss complex suspect descriptions

---

## Common Issues

### "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install -r requirements.txt
```

### "Missing required columns"
Your Excel file needs columns named exactly:
- `crime_code`
- `narrative`

### "API key not configured" (but you set it)
Make sure you:
1. Set it in the same terminal where you run the script
2. Or edit `config.py` directly
3. Restart terminal after setting environment variable

---

## What Next?

- Check the `output/` folder for results
- Review statistics at the end of processing
- Read full README.md for advanced options
- Customize extraction in `config.py`

---

**Need help?** Check README.md or review error messages in terminal.
