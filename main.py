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
            
            # Set up dialog handler for browser-level dialogs
            async def dialog_handler(dialog):
                self.logger.info(f"Dialog detected: {dialog.type} - {dialog.message}")
                if "location" in dialog.message.lower() or "allow" in dialog.message.lower():
                    self.logger.info("Accepting location permission dialog")
                    await dialog.accept()
                else:
                    self.logger.info("Dismissing non-location dialog")
                    await dialog.dismiss()
            
            # Add dialog listener
            self.page.on("dialog", dialog_handler)
            
            # Wait a moment for any dialogs to appear
            await asyncio.sleep(2)
            
            # Check for common location permission selectors on the page
            location_selectors = [
                'button:has-text("Allow")',
                'button:has-text("Enable Location")',
                'button:has-text("Share Location")',
                '[data-testid*="location"]',
                '[class*="location"][class*="allow"]',
                '.location-permission button',
                '[aria-label*="location"]',
                'button[class*="location"]'
            ]
            
            for selector in location_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Check if element is visible and contains location-related text
                        if await element.is_visible():
                            text_content = await element.text_content()
                            if text_content and any(keyword in text_content.lower() for keyword in ['allow', 'enable', 'location', 'share']):
                                self.logger.info(f"Found location permission button: {text_content}")
                                await element.click()
                                self.logger.info("Clicked location permission button")
                                
                                # Wait for any changes after clicking
                                await asyncio.sleep(1)
                                break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} not found or not clickable: {e}")
                    continue
            
            # Remove dialog listener
            self.page.remove_listener("dialog", dialog_handler)
            
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
            
            # Take screenshot for verification
            await self.take_screenshot("task1_bestbuy_homepage.png")
            
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