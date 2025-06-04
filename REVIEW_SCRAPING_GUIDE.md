# 🔍 Review Scraping Guide - Phase 2 Only

This guide shows you **all the ways to run only the review scraping part** (Phase 2) of the Best Buy automation.

## ✅ Prerequisites

Before running review scraping, ensure:

1. **Phase 1 is completed**: File `data/laptop_products_all_pages.json` exists
2. **Virtual environment activated**: `source .venv/bin/activate`
3. **All dependencies installed** in `.venv`

## 🚀 4 Ways to Run Review Scraping Only

### 1. 🔥 Interactive Launcher (Recommended for beginners)

```bash
source .venv/bin/activate
python launcher.py
```

Then select **option 2**: "Phase 2: Review Scraping"

**Benefits:**
- User-friendly menu
- Automatic prerequisite checking
- Clear guidance and error messages

---

### 2. ⚡ Direct Script (Recommended for production)

```bash
source .venv/bin/activate
python run_review_scraping_only.py
```

**Benefits:**
- Dedicated script just for review scraping
- Built-in validation and error handling
- Detailed progress reporting
- Clean, focused execution

---

### 3. 🔧 Main Script with Reviews Argument

```bash
source .venv/bin/activate
python main.py reviews
```

**Benefits:**
- Uses the original main script
- Command-line friendly
- Good for automation/scripting

---

### 4. 🧪 Test Mode (Small subset first)

```bash
source .venv/bin/activate
python test_review_scraping.py
```

**Benefits:**
- Tests on first 3 products only
- Quick validation (5-10 minutes)
- Good for testing before full run
- Shows detailed statistics

## 🎯 What Review Scraping Does

### Core Features

✅ **Handles country selection** - Automatically selects "United States"  
✅ **Smart scrolling** - Scrolls to 75% of page to load review button  
✅ **Review pagination** - Automatically clicks through all review pages  
✅ **Comprehensive extraction** - Gets title and description for each review  
✅ **Error handling** - Screenshots and logs for debugging  

### Advanced Pagination Handling

The review scraper now handles multiple pages of reviews:

- Detects `<li class="page next">` pagination elements
- Automatically clicks through all review pages
- Collects reviews from every page
- Stops when no more pages are found
- **Example**: Product with 200+ reviews across 10+ pages ✅

## 📊 Expected Results

### Processing Time
- **~115 products**: 20-30 minutes total
- **Per product**: 10-20 seconds (depending on review count)
- **With pagination**: Additional time for multiple review pages

### Output Files
- **Input**: `data/laptop_products_all_pages.json`
- **Output**: `data/laptop_products_with_reviews.json`
- **Screenshots**: `data/*.png` (for verification)
- **Logs**: `logs/automation.log`

### Sample Statistics (from test run)
```
✅ Total products tested: 3
✅ Total reviews found: 418
📊 Review statistics:
   Max reviews per product: 200
   Min reviews per product: 18  
   Average reviews per product: 139.3
```

## 📋 Step-by-Step Instructions

### For First-Time Users

1. **Verify prerequisites**:
   ```bash
   ls data/laptop_products_all_pages.json  # Should exist
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Run interactive launcher**:
   ```bash
   python launcher.py
   ```

4. **Select option 2** when prompted

5. **Monitor progress** in terminal output

6. **Check results**:
   ```bash
   ls data/laptop_products_with_reviews.json
   ```

### For Production Use

```bash
# Quick one-liner for production
source .venv/bin/activate && python run_review_scraping_only.py
```

### For Testing

```bash
# Test on 3 products first
source .venv/bin/activate && python test_review_scraping.py
```

## 🔧 Troubleshooting

### "Required input file not found"
```bash
# Run Phase 1 first to generate the input file
python main.py
```

### Browser/Playwright Issues
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Check if Playwright browsers are installed
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

### Slow Performance
- **Normal behavior**: Each product page must be visited individually
- **With pagination**: Products with many reviews take longer
- **Test first**: Use `python test_review_scraping.py` to validate

### Process Interrupted
- **Resume**: Simply run the script again
- **Progress**: Check logs in `logs/automation.log`
- **Partial results**: Previous successful scraping is preserved

## 📁 Output Format

Each product in the output file includes:

```json
{
  "product_name": "Laptop Name",
  "product_price": "$999.99", 
  "rating": "90%",
  "number_of_reviews": "123",
  "product_url": "https://www.bestbuy.com/site/...",
  "reviews": [
    {
      "title": "Great laptop!",
      "description": "Very fast and reliable for daily use..."
    },
    {
      "title": "Excellent build quality", 
      "description": "Solid construction and great performance..."
    }
  ]
}
```

## 🎉 Success Indicators

Look for these signs of successful completion:

✅ `✅ PHASE 2 COMPLETED SUCCESSFULLY!`  
✅ `📁 Output saved to: data/laptop_products_with_reviews.json`  
✅ `💬 Total reviews scraped: [large number]`  
✅ `📸 Screenshots saved in the data/ directory`  

---

**Need help?** Check `logs/automation.log` for detailed information or run the test mode first! 