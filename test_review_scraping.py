"""
Test Review Scraping Script
Tests the review scraping functionality on a small subset of products.
Now includes pagination handling for reviews.
"""

import asyncio
import json
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import BestBuyAutomation
import config


async def test_review_scraping():
    """Test review scraping on the first 3 products."""
    automation = BestBuyAutomation()
    
    try:
        print("=== Testing Review Scraping with Pagination (First 3 Products) ===")
        print("🔄 Now handles multiple pages of reviews per product")
        print("📄 Will navigate through all review pages automatically")
        
        # Launch browser
        await automation.launch_browser()
        
        # Load products from JSON
        products = await automation.load_products_from_json("laptop_products_all_pages.json")
        
        print(f"Loaded {len(products)} products from JSON file")
        print("Testing review scraping on first 3 products...\n")
        
        test_products = []
        
        for i, product in enumerate(products[:3]):  # Test only first 3 products
            try:
                print(f"Testing product {i+1}/3: {product.get('product_name', 'Unknown')[:50]}...")
                
                if not product.get('url'):
                    print(f"Skipping product {i+1} - no URL available")
                    continue
                
                # Create enhanced product data structure
                enhanced_product = {
                    "product_name": product.get('product_name', ''),
                    "product_price": product.get('price', ''),
                    "rating": product.get('rating', ''),
                    "number_of_reviews": product.get('number_of_reviews', ''),
                    "product_url": product.get('url', ''),
                    "reviews": []
                }
                
                # Scrape reviews for this product (now with pagination)
                reviews = await automation.scrape_product_reviews(
                    product.get('url', ''),
                    product.get('product_name', f'Product {i+1}')
                )
                
                enhanced_product["reviews"] = reviews
                test_products.append(enhanced_product)
                
                print(f"✅ Product {i+1}: Found {len(reviews)} reviews across all pages")
                
                # Show first review as example
                if reviews:
                    first_review = reviews[0]
                    print(f"   Sample review - Title: {first_review.get('title', 'N/A')[:40]}...")
                    print(f"   Sample review - Description: {first_review.get('description', 'N/A')[:60]}...")
                
                # Show pagination info if available
                if len(reviews) > 5:  # Likely paginated if more than 5 reviews
                    print(f"   📄 Note: This product likely had multiple review pages")
                
                print()
                
            except Exception as e:
                print(f"❌ Error testing product {i+1}: {e}")
                continue
        
        # Save test results
        test_file = config.DATA_DIR / "test_products_with_reviews.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_products, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test completed! Results saved to: {test_file}")
        print(f"✅ Total products tested: {len(test_products)}")
        
        total_reviews = sum(len(product.get('reviews', [])) for product in test_products)
        print(f"✅ Total reviews found: {total_reviews}")
        
        # Show statistics
        if test_products:
            max_reviews = max(len(product.get('reviews', [])) for product in test_products)
            min_reviews = min(len(product.get('reviews', [])) for product in test_products)
            avg_reviews = total_reviews / len(test_products)
            
            print(f"📊 Review statistics:")
            print(f"   Max reviews per product: {max_reviews}")
            print(f"   Min reviews per product: {min_reviews}")
            print(f"   Average reviews per product: {avg_reviews:.1f}")
        
        if test_products:
            print("\n=== Sample Output Structure ===")
            sample_product = test_products[0]
            print(json.dumps(sample_product, indent=2)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    finally:
        await automation.cleanup()
        
    return 0


if __name__ == "__main__":
    print("Starting review scraping test with pagination support...")
    exit_code = asyncio.run(test_review_scraping())
    exit(exit_code) 