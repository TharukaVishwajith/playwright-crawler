"""
E-Commerce Analytics Automation - Main Script
Task 1: Initial Setup and Navigation
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError, Playwright

import config


class BestBuyAutomation:
    """Main automation class for Best Buy e-commerce analytics."""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        # Ensure logs directory exists
        config.LOGS_DIR.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, config.LOGGING_CONFIG["level"]),
            format=config.LOGGING_CONFIG["format"],
            handlers=[
                logging.FileHandler(config.LOGGING_CONFIG["filename"]),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def launch_browser(self) -> None:
        """
        Launch Firefox browser in headless mode with robust configuration.
        Task 1: Initial Setup
        Note: Using Firefox instead of Chromium due to system compatibility issues
        """
        try:
            self.logger.info("Launching Firefox browser in headless mode...")
            
            self.playwright = await async_playwright().start()
            
            # Launch Firefox browser with minimal configuration
            self.browser = await self.playwright.firefox.launch(
                headless=config.BROWSER_CONFIG["headless"]
            )
            
            # Create browser context with viewport and user agent
            self.context = await self.browser.new_context(
                viewport=config.BROWSER_CONFIG["viewport"],
                user_agent=config.BROWSER_CONFIG["user_agent"]
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Set default timeouts
            self.page.set_default_timeout(config.DEFAULT_TIMEOUT)
            self.page.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)
            
            self.logger.info("Browser launched successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to launch browser: {e}")
            raise
            
    async def navigate_to_bestbuy(self) -> None:
        """
        Navigate to Best Buy website with robust wait strategy.
        Task 1: Navigation
        """
        try:
            self.logger.info(f"Navigating to {config.BASE_URL}...")
            
            # Navigate to Best Buy with wait for load state
            await self.page.goto(
                config.BASE_URL, 
                wait_until="domcontentloaded",
                timeout=config.NAVIGATION_TIMEOUT
            )
            
            # Implement robust wait strategy for dynamic elements
            await self.wait_for_page_ready()
            
            # Handle country selection if it appears
            await self.handle_country_selection()
            
            # Handle location permission alert if it appears
            await self.handle_location_permission()
            
            self.logger.info("Successfully navigated to Best Buy")
            
        except PlaywrightTimeoutError:
            self.logger.error("Timeout while navigating to Best Buy")
            raise
        except Exception as e:
            self.logger.error(f"Failed to navigate to Best Buy: {e}")
            raise
            
    async def handle_country_selection(self) -> None:
        """
        Handle the country selection screen if it appears.
        Looks for "Choose a country." H1 and clicks on "United States" H4.
        """
        try:
            self.logger.info("Checking for country selection screen...")
            
            # Check if the country selection screen is present
            country_selection_header = await self.page.query_selector('h1:has-text("Choose a country.")')
            
            if country_selection_header:
                self.logger.info("Country selection screen detected")
                
                # Look for the United States option
                us_option = await self.page.query_selector('h4:has-text("United States")')
                
                if us_option:
                    self.logger.info("Clicking on United States option...")
                    
                    # Click on the United States option
                    await us_option.click()
                    
                    # Wait for navigation after clicking
                    await self.page.wait_for_load_state("domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
                    
                    # Wait for the new page to be ready
                    await self.wait_for_page_ready()
                    
                    self.logger.info("Successfully selected United States and navigated to main site")
                else:
                    self.logger.warning("United States option not found on country selection screen")
            else:
                self.logger.info("No country selection screen detected, proceeding with main site")
                
        except Exception as e:
            self.logger.error(f"Error handling country selection: {e}")
            # Don't raise the exception as this might not be critical
            self.logger.info("Continuing despite country selection handling error...")
            
    async def handle_location_permission(self) -> None:
        """
        Handle location permission alert/dialog if it appears.
        This can be a browser dialog or a website popup asking for location access.
        """
        try:
            self.logger.info("Checking for location permission dialog...")
            
            # Grant geolocation permission at browser context level
            await self.context.grant_permissions(['geolocation'])
            self.logger.info("Granted geolocation permission at browser context level")
            
            # Set up dialog handler for browser-level dialogs
            dialog_occurred = False
            
            async def dialog_handler(dialog):
                nonlocal dialog_occurred
                dialog_occurred = True
                self.logger.info(f"Dialog detected: {dialog.type} - {dialog.message}")
                try:
                    if dialog.type in ['alert', 'confirm'] and any(keyword in dialog.message.lower() for keyword in ['location', 'allow', 'permission', 'enable']):
                        self.logger.info("Accepting location-related dialog")
                        await dialog.accept()
                    else:
                        self.logger.info("Accepting dialog")
                        await dialog.accept()
                except Exception as e:
                    self.logger.error(f"Error handling dialog: {e}")
                    try:
                        await dialog.dismiss()
                    except:
                        pass
            
            # Add dialog listener
            self.page.on("dialog", dialog_handler)
            
            # Wait for potential dialogs and page popups
            await asyncio.sleep(3)
            
            # Check for common location permission selectors on the page
            location_selectors = [
                # Common location permission buttons
                'button:has-text("Allow")',
                'button:has-text("Block")',
                'button:has-text("Enable Location")',
                'button:has-text("Share Location")',
                'button:has-text("Not now")',
                'button:has-text("Later")',
                '[data-testid*="location"]',
                '[class*="location"]',
                '.location-permission button',
                '[aria-label*="location"]',
                'button[class*="location"]',
                # Generic modal/popup close buttons
                'button[aria-label="Close"]',
                'button[aria-label="close"]',
                '.modal button',
                '.popup button',
                '[role="dialog"] button',
                '.notification button',
                # Common dismiss patterns
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
                'button:has-text("X")',
                '.close-button',
                '.dismiss-button'
            ]
            
            popup_handled = False
            for selector in location_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            text_content = await element.text_content() or ""
                            self.logger.info(f"Found potential popup element: {text_content.strip()}")
                            
                            # Click allow/enable buttons or dismiss buttons
                            if any(keyword in text_content.lower() for keyword in ['allow', 'enable', 'share', 'dismiss', 'close', 'not now', 'later', 'block']):
                                self.logger.info(f"Clicking location permission/popup button: {text_content.strip()}")
                                await element.click()
                                popup_handled = True
                                # Wait for popup to disappear
                                await asyncio.sleep(2)
                                break
                            # Handle X or close buttons
                            elif text_content.strip() in ['X', '×', ''] and 'close' in selector.lower():
                                self.logger.info(f"Clicking close button")
                                await element.click()
                                popup_handled = True
                                await asyncio.sleep(2)
                                break
                                
                    if popup_handled:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Selector {selector} not found or not clickable: {e}")
                    continue
            
            # Try to dismiss any remaining overlays by pressing Escape
            if not popup_handled and not dialog_occurred:
                self.logger.info("No popup buttons found, trying Escape key to dismiss overlays")
                await self.page.keyboard.press('Escape')
                await asyncio.sleep(1)
            
            # Remove dialog listener
            self.page.remove_listener("dialog", dialog_handler)
            
            # Take a screenshot to see current state
            try:
                await self.take_screenshot("after_location_handling.png")
            except:
                pass
            
            self.logger.info("Location permission handling completed")
            
        except Exception as e:
            self.logger.error(f"Error handling location permission: {e}")
            # Don't raise the exception as this might not be critical
            self.logger.info("Continuing despite location permission handling error...")
            
    async def wait_for_page_ready(self) -> None:
        """
        Implement robust wait strategy for dynamic elements.
        Task 1: Robust wait strategy
        """
        try:
            self.logger.info("Waiting for page to be fully loaded...")
            
            # Wait for network to be idle (reduced timeout for faster execution)
            try:
                await self.page.wait_for_load_state("networkidle", timeout=15000)
                self.logger.info("Network is idle")
            except Exception as e:
                self.logger.warning(f"Network idle timeout: {e}")
            
            # Wait for common Best Buy elements to ensure page is loaded
            selectors_to_wait = [
                'header',                 # Main header (simplified selector)
                'nav',                    # Navigation menu
                'main, #main, [role="main"]',  # Main content area with fallbacks
            ]
            
            elements_found = 0
            for selector in selectors_to_wait:
                try:
                    await self.page.wait_for_selector(
                        selector, 
                        timeout=config.ELEMENT_WAIT_TIMEOUT,
                        state="visible"
                    )
                    self.logger.debug(f"Found element: {selector}")
                    elements_found += 1
                except Exception as e:
                    self.logger.warning(f"Element not found within timeout: {selector} - {e}")
            
            # Continue if we found at least one element
            if elements_found > 0:
                self.logger.info(f"Found {elements_found} out of {len(selectors_to_wait)} expected elements")
            else:
                self.logger.warning("No expected elements found, but continuing...")
            
            # Additional wait for any dynamic content
            await asyncio.sleep(config.PAGE_LOAD_DELAY)
            
            # Verify we're on the correct site
            current_url = self.page.url
            if "bestbuy.com" not in current_url:
                raise Exception(f"Unexpected URL: {current_url}")
                
            self.logger.info("Page is fully loaded and ready")
            
        except Exception as e:
            self.logger.error(f"Error waiting for page ready: {e}")
            raise
            
    async def take_screenshot(self, filename: str = "task1_screenshot.png") -> None:
        """Take a screenshot for verification purposes."""
        try:
            screenshot_path = config.DATA_DIR / filename
            config.DATA_DIR.mkdir(exist_ok=True)
            
            await self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            
    async def get_page_info(self) -> dict:
        """Get basic page information for verification."""
        try:
            page_info = {
                "url": self.page.url,
                "title": await self.page.title(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.logger.info(f"Page info: {page_info}")
            return page_info
            
        except Exception as e:
            self.logger.error(f"Failed to get page info: {e}")
            return {}
            
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
                
            self.logger.info("Browser cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    async def search_laptops_and_filter(self) -> None:
        """
        Perform laptop search and apply price filtering.
        Steps:
        1. Search for "laptop"
        2. Wait for results to load
        3. Set price range (500-1500)
        4. Apply the filter
        """
        try:
            self.logger.info("=== Starting laptop search and price filtering ===")
            
            # Debug: Take a screenshot to see current page state
            await self.take_screenshot("before_search.png")
            
            # Step 1: Type "laptop" in the search input field with multiple selector options
            self.logger.info("Step 1: Searching for 'laptop'...")
            
            search_selectors = [
                'input.sugg-search-bar-input[data-testid="SearchBar-TestID"]',
                'input[data-testid="SearchBar-TestID"]',
                'input[placeholder*="Search"]',
                'input[id*="search"]',
                'input[class*="search"]',
                'input[autocomplete-search-bar]',
                '#autocomplete-search-bar',
                'input.search-input',
                '[role="searchbox"]',
                'input[type="search"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    self.logger.info(f"Trying search selector: {selector}")
                    search_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if search_input:
                        self.logger.info(f"Found search input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Search selector {selector} failed: {e}")
                    continue
            
            if not search_input:
                # Debug: Print available input elements
                self.logger.info("Search input not found, checking all input elements...")
                inputs = await self.page.query_selector_all('input')
                for i, input_elem in enumerate(inputs):
                    try:
                        if await input_elem.is_visible():
                            placeholder = await input_elem.get_attribute('placeholder') or ''
                            id_attr = await input_elem.get_attribute('id') or ''
                            class_attr = await input_elem.get_attribute('class') or ''
                            self.logger.info(f"Input {i}: placeholder='{placeholder}', id='{id_attr}', class='{class_attr}'")
                    except:
                        pass
                raise Exception("Search input field not found")
            
            # Clear any existing text and type "laptop"
            await search_input.fill("laptop")
            self.logger.info("Typed 'laptop' in search field")
            
            # Step 2: Click the search button with multiple selector options
            self.logger.info("Step 2: Clicking search button...")
            
            button_selectors = [
                'button#autocomplete-search-button[data-testid="SearchButton-TestID"]',
                'button[data-testid="SearchButton-TestID"]',
                'button[aria-label*="Search"]',
                'button.sugg-magnifier',
                'button[id*="search"]',
                'button[class*="search"]',
                '[role="button"][aria-label*="Search"]',
                'button:has-text("Search")',
                '.search-button'
            ]
            
            search_button = None
            for selector in button_selectors:
                try:
                    self.logger.info(f"Trying button selector: {selector}")
                    search_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if search_button:
                        self.logger.info(f"Found search button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Button selector {selector} failed: {e}")
                    continue
            
            if not search_button:
                # Alternative: Press Enter on the search input
                self.logger.info("Search button not found, trying Enter key...")
                await search_input.press('Enter')
            else:
                await search_button.click()
            
            self.logger.info("Search submitted")
            
            # Step 3: Wait 15 seconds for the page to load
            self.logger.info("Step 3: Waiting 15 seconds for search results to load...")
            await asyncio.sleep(15)
            
            # Additional wait for page to be ready
            await self.page.wait_for_load_state("domcontentloaded")
            self.logger.info("Search results page loaded")
            
            # Debug: Take screenshot of search results
            await self.take_screenshot("search_results.png")
            
            # Step 4: Set minimum price to 500
            self.logger.info("Step 4: Setting minimum price to 500...")
            
            min_price_selectors = [
                'input[placeholder="Min Price"]',
                'input[placeholder*="Min"]',
                'input[data-testid*="min"]',
                'input[aria-label*="minimum"]',
                '.price-filter input[type="number"]:first-child',
                '.min-price input'
            ]
            
            min_price_input = None
            for selector in min_price_selectors:
                try:
                    min_price_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if min_price_input:
                        self.logger.info(f"Found min price input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Min price selector {selector} failed: {e}")
                    continue
            
            if not min_price_input:
                raise Exception("Min price input field not found")
                
            await min_price_input.fill("500")
            self.logger.info("Set minimum price to 500")
            
            # Step 5: Set maximum price to 1500
            self.logger.info("Step 5: Setting maximum price to 1500...")
            
            max_price_selectors = [
                'input[placeholder="Max Price"]',
                'input[placeholder*="Max"]',
                'input[data-testid*="max"]',
                'input[aria-label*="maximum"]',
                '.price-filter input[type="number"]:last-child',
                '.max-price input'
            ]
            
            max_price_input = None
            for selector in max_price_selectors:
                try:
                    max_price_input = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if max_price_input:
                        self.logger.info(f"Found max price input with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Max price selector {selector} failed: {e}")
                    continue
            
            if not max_price_input:
                raise Exception("Max price input field not found")
                
            await max_price_input.fill("1500")
            self.logger.info("Set maximum price to 1500")
            
            # Step 6: Click the "Set" button to apply price filter
            self.logger.info("Step 6: Applying price filter...")
            
            set_button_selectors = [
                'button.current-price-facet-set-button:has-text("Set")',
                'button:has-text("Set")',
                'button[aria-label*="Set"]',
                '.price-filter button:has-text("Set")',
                '.price-facet button:has-text("Set")',
                'button.set-button'
            ]
            
            set_button = None
            for selector in set_button_selectors:
                try:
                    set_button = await self.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if set_button:
                        self.logger.info(f"Found set button with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Set button selector {selector} failed: {e}")
                    continue
            
            if not set_button:
                raise Exception("Set button not found")
                
            await set_button.click()
            self.logger.info("Clicked 'Set' button to apply price filter")
            
            # Wait for filter to be applied
            await asyncio.sleep(3)
            await self.page.wait_for_load_state("domcontentloaded")
            
            # Final screenshot
            await self.take_screenshot("final_filtered_results.png")
            
            self.logger.info("=== Laptop search and price filtering completed successfully ===")
            
        except Exception as e:
            self.logger.error(f"Error during laptop search and filtering: {e}")
            # Take screenshot for debugging
            try:
                await self.take_screenshot("error_state.png")
            except:
                pass
            raise
            
    async def run_task_1(self) -> dict:
        """
        Execute Task 1: Initial Setup and Navigation
        Returns page information for verification
        """
        try:
            self.logger.info("=== Starting Task 1: Initial Setup and Navigation ===")
            
            # Launch browser
            await self.launch_browser()
            
            # Navigate to Best Buy
            await self.navigate_to_bestbuy()
            
            # Perform laptop search and price filtering
            await self.search_laptops_and_filter()
            
            # Take screenshot for verification
            await self.take_screenshot("task1_laptop_search_filtered.png")
            
            # Get page information
            page_info = await self.get_page_info()
            
            self.logger.info("=== Task 1 completed successfully ===")
            return page_info
            
        except Exception as e:
            self.logger.error(f"Task 1 failed: {e}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point for the automation script."""
    automation = BestBuyAutomation()
    
    try:
        result = await automation.run_task_1()
        print(f"Task 1 completed successfully!")
        print(f"Page URL: {result.get('url', 'N/A')}")
        print(f"Page Title: {result.get('title', 'N/A')}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
        
    except Exception as e:
        print(f"Task 1 failed: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    # Run the automation
    exit_code = asyncio.run(main())
    exit(exit_code) 