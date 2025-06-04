"""
E-Commerce Analytics Automation - Review Scraping Script
Task 2: Review Scraping for All Products

This script loads products from laptop_products_all_pages.json and scrapes
customer reviews for each product, creating an enhanced JSON file with reviews.
"""

import asyncio
import sys
import os

# Add the current directory to the Python path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import BestBuyAutomation


async def main():
    """Main entry point for the review scraping script."""
    automation = BestBuyAutomation()
    
    try:
        print("=== Best Buy Review Scraping Task ===")
        print("Loading products from laptop_products_all_pages.json...")
        print("This process will visit each product page and scrape customer reviews.")
        print("Please be patient as this may take some time...\n")
        
        result = await automation.run_review_scraping_task()
        
        print("\n=== Review Scraping Completed Successfully! ===")
        print(f"✅ Total products processed: {result.get('total_products_processed', 'N/A')}")
        print(f"✅ Products with reviews found: {result.get('products_with_reviews', 'N/A')}")
        print(f"✅ Total reviews scraped: {result.get('total_reviews_scraped', 'N/A')}")
        print(f"✅ Average reviews per product: {result.get('average_reviews_per_product', 'N/A')}")
        print(f"✅ Output file: data/laptop_products_with_reviews.json")
        print(f"✅ Completed at: {result.get('timestamp', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Review scraping task failed: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    # Run the review scraping automation
    exit_code = asyncio.run(main())
    exit(exit_code) 