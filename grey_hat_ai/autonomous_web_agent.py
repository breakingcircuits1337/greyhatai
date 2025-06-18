"""
Autonomous Web Agent Tool for Grey Hat AI

This module provides a Playwright-based web automation tool that can be used
by the CAI agent for web-based reconnaissance and testing tasks.
"""

import os
import logging
import asyncio
import base64
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import json
import tempfile

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    BrowserContext = None
    PlaywrightTimeoutError = Exception

logger = logging.getLogger(__name__)


@dataclass
class WebAgentConfig:
    """Configuration for the autonomous web agent."""
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    timeout: int = 30000  # milliseconds
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Security settings
    ignore_https_errors: bool = True
    disable_web_security: bool = True
    
    # Performance settings
    disable_images: bool = False
    disable_javascript: bool = False


class AutonomousWebAgent:
    """
    Autonomous web agent using Playwright for browser automation.
    
    Provides capabilities for:
    - Web navigation and interaction
    - Form filling and submission
    - Content extraction and analysis
    - Screenshot capture
    - Cookie and session management
    """
    
    def __init__(self, config: WebAgentConfig = None):
        self.config = config or WebAgentConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the web agent and browser.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self._is_initialized:
            return True
            
        if not async_playwright:
            logger.error("Playwright not available")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            if self.config.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-web-security" if self.config.disable_web_security else "",
                        "--ignore-certificate-errors" if self.config.ignore_https_errors else ""
                    ]
                )
            elif self.config.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.config.headless
                )
            elif self.config.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.config.headless
                )
            else:
                raise ValueError(f"Unsupported browser type: {self.config.browser_type}")
            
            # Create context
            self.context = await self.browser.new_context(
                viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
                user_agent=self.config.user_agent,
                ignore_https_errors=self.config.ignore_https_errors
            )
            
            # Configure context
            if self.config.disable_images:
                await self.context.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())
            
            # Create page
            self.page = await self.context.new_page()
            await self.page.set_default_timeout(self.config.timeout)
            
            self._is_initialized = True
            logger.info("Web agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize web agent: {e}")
            await self.cleanup()
            return False
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self._is_initialized = False
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
    
    async def navigate(self, url: str, wait_for: str = "load") -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_for: What to wait for ("load", "domcontentloaded", "networkidle")
            
        Returns:
            Dictionary with navigation result
        """
        if not self._is_initialized:
            await self.initialize()
        
        try:
            response = await self.page.goto(url, wait_until=wait_for)
            
            return {
                "success": True,
                "url": self.page.url,
                "title": await self.page.title(),
                "status": response.status if response else None,
                "headers": dict(response.headers) if response else None
            }
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def get_page_content(self, content_type: str = "text") -> Dict[str, Any]:
        """
        Extract page content.
        
        Args:
            content_type: Type of content to extract ("text", "html", "markdown")
            
        Returns:
            Dictionary with extracted content
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            result = {
                "success": True,
                "url": self.page.url,
                "title": await self.page.title()
            }
            
            if content_type == "text":
                result["content"] = await self.page.inner_text("body")
            elif content_type == "html":
                result["content"] = await self.page.content()
            elif content_type == "markdown":
                # Simple HTML to markdown conversion
                text = await self.page.inner_text("body")
                result["content"] = text
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_elements(self, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Find elements on the page.
        
        Args:
            selector: CSS selector or XPath
            timeout: Timeout in milliseconds
            
        Returns:
            Dictionary with found elements
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            elements = await self.page.query_selector_all(selector)
            
            element_data = []
            for i, element in enumerate(elements):
                try:
                    element_info = {
                        "index": i,
                        "tag": await element.evaluate("el => el.tagName.toLowerCase()"),
                        "text": await element.inner_text(),
                        "visible": await element.is_visible(),
                        "enabled": await element.is_enabled() if await element.evaluate("el => el.tagName.toLowerCase()") in ["input", "button", "select", "textarea"] else True
                    }
                    
                    # Get attributes
                    attributes = await element.evaluate("""
                        el => {
                            const attrs = {};
                            for (let attr of el.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }
                    """)
                    element_info["attributes"] = attributes
                    
                    element_data.append(element_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing element {i}: {e}")
                    continue
            
            return {
                "success": True,
                "count": len(element_data),
                "elements": element_data
            }
            
        except Exception as e:
            logger.error(f"Element finding error: {e}")
            return {"success": False, "error": str(e)}
    
    async def click_element(self, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Click an element.
        
        Args:
            selector: CSS selector or XPath
            timeout: Timeout in milliseconds
            
        Returns:
            Dictionary with click result
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            await self.page.click(selector, timeout=timeout)
            
            return {
                "success": True,
                "action": "click",
                "selector": selector,
                "url": self.page.url
            }
            
        except Exception as e:
            logger.error(f"Click error: {e}")
            return {"success": False, "error": str(e), "selector": selector}
    
    async def fill_form(self, form_data: Dict[str, str], submit: bool = False) -> Dict[str, Any]:
        """
        Fill a form with data.
        
        Args:
            form_data: Dictionary mapping selectors to values
            submit: Whether to submit the form after filling
            
        Returns:
            Dictionary with form filling result
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            filled_fields = []
            
            for selector, value in form_data.items():
                try:
                    await self.page.fill(selector, value)
                    filled_fields.append({"selector": selector, "value": value, "success": True})
                except Exception as e:
                    filled_fields.append({"selector": selector, "value": value, "success": False, "error": str(e)})
                    logger.warning(f"Failed to fill field {selector}: {e}")
            
            result = {
                "success": True,
                "filled_fields": filled_fields,
                "url": self.page.url
            }
            
            if submit:
                try:
                    # Try to find and click submit button
                    submit_selectors = [
                        "input[type='submit']",
                        "button[type='submit']",
                        "button:has-text('Submit')",
                        "button:has-text('Send')",
                        "button:has-text('Login')",
                        "input[value*='Submit']"
                    ]
                    
                    submitted = False
                    for submit_selector in submit_selectors:
                        try:
                            await self.page.click(submit_selector, timeout=2000)
                            result["submitted"] = True
                            submitted = True
                            break
                        except:
                            continue
                    
                    if not submitted:
                        # Try pressing Enter on the last filled field
                        if filled_fields:
                            last_field = filled_fields[-1]["selector"]
                            await self.page.press(last_field, "Enter")
                            result["submitted"] = True
                        else:
                            result["submitted"] = False
                            result["submit_error"] = "No submit button found"
                            
                except Exception as e:
                    result["submitted"] = False
                    result["submit_error"] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Form filling error: {e}")
            return {"success": False, "error": str(e)}
    
    async def take_screenshot(self, full_page: bool = False, path: str = None) -> Dict[str, Any]:
        """
        Take a screenshot of the page.
        
        Args:
            full_page: Whether to capture the full page
            path: Path to save screenshot (optional)
            
        Returns:
            Dictionary with screenshot result
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            if path is None:
                # Create temporary file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    path = tmp_file.name
            
            await self.page.screenshot(path=path, full_page=full_page)
            
            # Read screenshot as base64 for embedding
            with open(path, "rb") as f:
                screenshot_data = base64.b64encode(f.read()).decode()
            
            return {
                "success": True,
                "path": path,
                "base64": screenshot_data,
                "url": self.page.url,
                "full_page": full_page
            }
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """
        Execute JavaScript on the page.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Dictionary with execution result
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            result = await self.page.evaluate(script)
            
            return {
                "success": True,
                "result": result,
                "script": script,
                "url": self.page.url
            }
            
        except Exception as e:
            logger.error(f"JavaScript execution error: {e}")
            return {"success": False, "error": str(e), "script": script}
    
    async def wait_for_element(self, selector: str, timeout: int = 30000, state: str = "visible") -> Dict[str, Any]:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector or XPath
            timeout: Timeout in milliseconds
            state: Element state to wait for ("visible", "hidden", "attached", "detached")
            
        Returns:
            Dictionary with wait result
        """
        if not self.page:
            return {"success": False, "error": "Page not initialized"}
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            
            return {
                "success": True,
                "selector": selector,
                "state": state,
                "url": self.page.url
            }
            
        except PlaywrightTimeoutError:
            return {
                "success": False,
                "error": f"Timeout waiting for element: {selector}",
                "selector": selector,
                "timeout": timeout
            }
        except Exception as e:
            logger.error(f"Wait for element error: {e}")
            return {"success": False, "error": str(e), "selector": selector}
    
    async def get_cookies(self) -> Dict[str, Any]:
        """Get all cookies for the current page."""
        if not self.context:
            return {"success": False, "error": "Context not initialized"}
        
        try:
            cookies = await self.context.cookies()
            return {
                "success": True,
                "cookies": cookies,
                "count": len(cookies)
            }
        except Exception as e:
            logger.error(f"Get cookies error: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Set cookies for the current context."""
        if not self.context:
            return {"success": False, "error": "Context not initialized"}
        
        try:
            await self.context.add_cookies(cookies)
            return {
                "success": True,
                "cookies_set": len(cookies)
            }
        except Exception as e:
            logger.error(f"Set cookies error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the web agent."""
        return {
            "initialized": self._is_initialized,
            "playwright_available": async_playwright is not None,
            "current_url": self.page.url if self.page else None,
            "browser_type": self.config.browser_type,
            "headless": self.config.headless
        }


# CAI Tool Integration
def create_web_agent_tool():
    """Create a CAI tool for the autonomous web agent."""
    
    # Global web agent instance
    _web_agent = None
    
    async def get_web_agent():
        nonlocal _web_agent
        if _web_agent is None:
            _web_agent = AutonomousWebAgent()
            await _web_agent.initialize()
        return _web_agent
    
    def web_navigate(url: str, wait_for: str = "load") -> str:
        """Navigate to a URL and return page information."""
        async def _navigate():
            agent = await get_web_agent()
            result = await agent.navigate(url, wait_for)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_navigate())
    
    def web_get_content(content_type: str = "text") -> str:
        """Extract content from the current page."""
        async def _get_content():
            agent = await get_web_agent()
            result = await agent.get_page_content(content_type)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_get_content())
    
    def web_find_elements(selector: str) -> str:
        """Find elements on the page using CSS selector."""
        async def _find_elements():
            agent = await get_web_agent()
            result = await agent.find_elements(selector)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_find_elements())
    
    def web_click(selector: str) -> str:
        """Click an element on the page."""
        async def _click():
            agent = await get_web_agent()
            result = await agent.click_element(selector)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_click())
    
    def web_fill_form(form_data_json: str, submit: bool = False) -> str:
        """Fill a form with data. form_data_json should be a JSON string mapping selectors to values."""
        async def _fill_form():
            agent = await get_web_agent()
            try:
                form_data = json.loads(form_data_json)
                result = await agent.fill_form(form_data, submit)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return json.dumps({"success": False, "error": f"Invalid JSON: {e}"})
        
        return asyncio.run(_fill_form())
    
    def web_screenshot(full_page: bool = False, save_path: str = None) -> str:
        """Take a screenshot of the current page."""
        async def _screenshot():
            agent = await get_web_agent()
            result = await agent.take_screenshot(full_page, save_path)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_screenshot())
    
    def web_execute_js(script: str) -> str:
        """Execute JavaScript on the current page."""
        async def _execute_js():
            agent = await get_web_agent()
            result = await agent.execute_javascript(script)
            return json.dumps(result, indent=2)
        
        return asyncio.run(_execute_js())
    
    # Return tool functions that can be registered with CAI
    return {
        "web_navigate": web_navigate,
        "web_get_content": web_get_content,
        "web_find_elements": web_find_elements,
        "web_click": web_click,
        "web_fill_form": web_fill_form,
        "web_screenshot": web_screenshot,
        "web_execute_js": web_execute_js
    }

