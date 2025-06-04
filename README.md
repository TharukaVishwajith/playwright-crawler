# Best Buy E-Commerce Analytics Automation

This project automates the scraping of Best Buy laptop products and their customer reviews in **two distinct phases**.

## Prerequisites

1. Ensure you have Python 3.8+ installed
2. Activate the virtual environment: `source .venv/bin/activate`
3. All dependencies should already be installed in the `.venv`

## 🚀 Quick Start - Run Only Review Scraping (Phase 2)

If you already have the product data from Phase 1 and **only want to run the review scraping**:

### Option 1: Interactive Launcher (Recommended)
```bash
source .venv/bin/activate
python launcher.py
# Then select option 2: "Phase 2: Review Scraping"
```

### Option 2: Direct Script
```bash
source .venv/bin/activate
python run_review_scraping_only.py
```

### Option 3: Using Main Script
```bash
source .venv/bin/activate
python main.py reviews
```

### Option 4: Test First (3 products only)
```bash
source .venv/bin/activate
python test_review_scraping.py
```

## Two-Phase Automation Details

### Phase 1: Product Listing Scraping
Scrapes laptop products from Best Buy search results with filters applied.

**Output**: `data/laptop_products_all_pages.json`

**To run Phase 1 only**:
```bash
python main.py
```

### Phase 2: Product Review Scraping ⭐
Loads products from Phase 1 and scrapes customer reviews for each product.

**Input**: `data/laptop_products_all_pages.json`  
**Output**: `data/laptop_products_with_reviews.json`

**Multiple ways to run Phase 2 only**:

| Method | Command | Best For |
|--------|---------|----------|
| **Interactive Menu** | `python launcher.py` | First-time users |
| **Direct Script** | `python run_review_scraping_only.py` | Production use |
| **Main Script** | `python main.py reviews` | Command line |
| **Test Mode** | `python test_review_scraping.py` | Testing/debugging |

## Output Format

### Phase 1 Output Structure
```json
[
  {
    "product_name": "Laptop Name",
    "price": "$999.99",
    "rating": "90%", 
    "number_of_reviews": "123",
    "url": "https://www.bestbuy.com/site/..."
  }
]
```

### Phase 2 Output Structure
```json
[
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
      }
    ]
  }
]
```

## 📋 Step-by-Step Guide for Review Scraping Only

1. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Verify Phase 1 data exists**:
   ```bash
   ls data/laptop_products_all_pages.json
   ```

3. **Choose your preferred method**:

   **🔥 Recommended - Interactive Launcher**:
   ```bash
   python launcher.py
   ```
   
   **⚡ Quick - Direct Script**:
   ```bash
   python run_review_scraping_only.py
   ```

4. **Monitor progress**:
   - Watch console output for real-time progress
   - Check `logs/automation.log` for detailed logs
   - Screenshots saved in `data/` directory

5. **Check results**:
   ```bash
   ls data/laptop_products_with_reviews.json
   ```

## Files Description

| File | Purpose | When to Use |
|------|---------|-------------|
| `launcher.py` | Interactive menu for all options | **First time or unsure what to run** |
| `run_review_scraping_only.py` | **Phase 2 only** with validation | **Production review scraping** |
| `main.py` | Original script (both phases) | Phase 1 or `main.py reviews` |
| `test_review_scraping.py` | Test on 3 products only | Testing before full run |
| `scrape_reviews.py` | Simple Phase 2 script | Alternative to above |

## ⚠️ Important Notes

- **Phase 2 requires Phase 1 to be completed first**
- Review scraping takes 20-30 minutes for ~115 products  
- Each product page is visited individually
- Process can be interrupted and resumed
- All progress is logged for debugging

## 🆘 Troubleshooting

**"Required input file not found"**:
- Run Phase 1 first: `python main.py`
- Or test with: `python test_review_scraping.py`

**Browser issues**:
- Make sure virtual environment is activated
- Check if Playwright browsers are installed in `.venv`

**Slow performance**:
- This is normal - each product page must be visited
- Use test mode first: `python test_review_scraping.py` 