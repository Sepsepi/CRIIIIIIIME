# Sample Data Information

## 📊 Available Sample Files

I've created **multiple sample data files** for you to test with:

---

### 1. **sample_crime_data_200_rows.xlsx** ⭐ RECOMMENDED
**200 realistic crime report narratives**

**What's included:**
- Diverse crime types (burglary, auto theft, commercial burglary, vehicle burglary)
- Various entry methods (window smash, door pry, unlocked, roof access, etc.)
- Suspect descriptions with different levels of detail
- Vehicle information (makes, models, colors, plates)
- Real-world scenarios based on actual police report patterns

**Use cases:**
- Full testing of the extraction system
- Performance benchmarking
- Quality metrics evaluation
- Representative of real data you'll process

**To use this file:**
```bash
# It's ready to go! Just run:
python main.py -i input/sample_crime_data_200_rows.xlsx
```

---

### 2. **sample_crime_data_realistic.xlsx**
**30 detailed crime narratives**

**What's included:**
- High-detail narratives
- Complex scenarios with multiple suspects
- Professional burglary crews
- Organized theft rings
- Technology-based crimes

**Use cases:**
- Testing complex extraction scenarios
- Verifying LLM handles detailed reports
- Smaller dataset for quick tests

**To use this file:**
```bash
python main.py -i input/sample_crime_data_realistic.xlsx
```

---

### 3. **crime_data.xlsx** (Original sample)
**5 basic crime narratives**

**What's included:**
- Simple, clean examples
- Basic burglary cases
- Vehicle theft examples
- Clear suspect/vehicle information

**Use cases:**
- Quick functionality test (5 rows process in seconds)
- Learning the system
- Demonstrating to others

**To use this file:**
```bash
# This is the default, so just run:
python main.py
```

---

## 🎯 Which Sample Should You Use?

### For Quick Testing (30 seconds)
```bash
python demo_quick_test.py
```
- Tests 3 narratives
- Shows extraction output
- Verifies API is working

### For Learning (1 minute)
```bash
python main.py
# Uses crime_data.xlsx (5 rows)
```
- See complete workflow
- Review statistics output
- Check Excel results

### For Full Testing (3-5 minutes)
```bash
python main.py -i input/sample_crime_data_200_rows.xlsx
```
- Realistic workload
- Comprehensive testing
- Full statistics report

---

## 📝 Sample Data Statistics

### Crime Types Included
- **220** - Burglary (residential)
- **459** - Burglary (commercial)
- **510** - Vehicle theft
- **330** - Burglary from vehicle

### Entry Methods Represented
- Window smash
- Door pry
- Door kick
- Unlocked entry
- Lock pick
- Roof/chimney access
- Fence cutting
- Electronic bypass
- Key duplication
- And many more...

### Suspect Information Variety
- Basic descriptions (height, clothing)
- Detailed descriptions (age, build, distinguishing features)
- Multiple suspects (S1, S2, S3)
- No suspect information
- Partial information

### Vehicle Information Variety
- Complete (make, model, color, plate)
- Partial (just color and make)
- License plate only
- No vehicle mentioned
- Multiple vehicles

---

## 🔄 Replace with Your Data

When ready to use your actual data:

1. **Prepare your Excel file** with these columns:
   - `crime_code` - The numeric crime code
   - `narrative` - The full narrative text

2. **Replace the sample file:**
   ```bash
   # Option 1: Replace the default file
   cp your_data.xlsx input/crime_data.xlsx
   python main.py

   # Option 2: Specify your file
   python main.py -i path/to/your_data.xlsx
   ```

3. **Check crime codes match:**
   - Review `input/crime_codes.csv`
   - Add any missing crime codes your data uses

---

## 🧪 Test Before Production

**Recommended testing workflow:**

```bash
# Step 1: Quick API test (30 seconds)
python demo_quick_test.py

# Step 2: Small sample (1 minute)
python main.py
# Check output/crime_data_extracted.xlsx

# Step 3: Larger sample (3-5 minutes)
python main.py -i input/sample_crime_data_200_rows.xlsx
# Review statistics and quality

# Step 4: Your real data
python main.py -i input/your_actual_data.xlsx
```

---

## 📊 Expected Results

### From sample_crime_data_200_rows.xlsx:

**Extraction rates (approximate):**
- Method of entry: ~90-95%
- Suspects found: ~35-40%
- Vehicles found: ~30-35%
- License plates: ~15-20%

**Why some fields lower?**
- Not every crime has suspects identified
- Not every crime involves a vehicle
- Many narratives don't include plates

**This is normal and matches real-world data patterns!**

---

## 💡 Understanding the Output

After running on sample data, you'll see:

### Console Output
```
==================================================================
🚔 CRIME REPORT EXTRACTOR
==================================================================
📂 Loading data from: input/sample_crime_data_200_rows.xlsx
✅ Loaded 200 crime reports
✅ Loaded 25 crime code mappings

🔄 Processing 200 crime reports...
Progress: 200/200 rows processed... ✅

💾 Saving results to: output/crime_data_extracted.xlsx
✅ Successfully saved 200 rows

📊 EXTRACTION STATISTICS
   Total rows processed:    200
   Successful extractions:  198
   Failed extractions:      2

   Method of entry found:   185 (92.5%)
   Suspects identified:     78 (39.0%)
   Vehicles found:          65 (32.5%)
```

### Excel Output
Check `output/crime_data_extracted.xlsx` with columns:
- Original: crime_code, narrative
- Extracted: crime_type, method_of_entry
- Suspects: suspect_1, suspect_2
- Vehicle: vehicle_make, vehicle_model, vehicle_color, vehicle_plate

---

## 🎯 Sample Data Features

### Realistic Scenarios
✅ Based on actual police report patterns
✅ Variety of detail levels (sparse to comprehensive)
✅ Multiple crime types and methods
✅ Edge cases (locked cars, technology crimes, organized crews)

### Testing Coverage
✅ Simple extractions (clear patterns)
✅ Complex extractions (multiple suspects, detailed narratives)
✅ Missing information (tests null handling)
✅ Ambiguous cases (tests LLM interpretation)

### Quality Assurance
✅ All rows have valid crime codes
✅ Narratives use realistic police language
✅ Mix of successful and challenging extractions
✅ Represents real-world data distribution

---

## 📞 Need Different Sample Data?

**Easy to customize!**

Edit the sample files directly in Excel:
1. Open `input/sample_crime_data_200_rows.xlsx`
2. Modify narratives to match your data format
3. Add/remove rows as needed
4. Save and run extraction

**Or create your own:**
1. Create Excel file with columns: `crime_code`, `narrative`
2. Add your sample data
3. Run: `python main.py -i your_sample.xlsx`

---

## ✅ You're All Set!

Your API key is configured and ready to use.

**Quick start now:**
```bash
cd crime_report_extractor
python demo_quick_test.py
```

**Full sample extraction:**
```bash
python main.py -i input/sample_crime_data_200_rows.xlsx
```

---

**Happy extracting! 🚔📊**
