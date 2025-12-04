import time
import random
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ===========================================
# CONFIGURATION - Change line number here
# https://x.com/i/flow/login
# bot.sannysoft.com
# ===========================================
ACCOUNT_LINE = 21  # Which line to use (1 = first line)
# ===========================================

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "x_credentials.txt")
PROXY_FILE = os.path.join(SCRIPT_DIR, "proxy_list.txt")


def load_credentials(line_number):
    """Load credentials from x_credentials.txt by line number."""
    with open(CREDENTIALS_FILE, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    if line_number < 1 or line_number > len(lines):
        raise ValueError(f"Invalid line number {line_number}. File has {len(lines)} lines.")
    
    line = lines[line_number - 1]
    parts = line.split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid format on line {line_number}: {line}")
    
    return {
        'x_username': parts[0],
        'x_password': parts[1],
        'outlook_email': parts[2],
        'outlook_password': parts[3]
    }


def load_proxy(line_number):
    """Load proxy from proxy_list.txt by line number."""
    with open(PROXY_FILE, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    if line_number < 1 or line_number > len(lines):
        raise ValueError(f"Invalid line number {line_number}. File has {len(lines)} lines.")
    
    line = lines[line_number - 1]
    parts = line.split(':')
    if len(parts) != 4:
        raise ValueError(f"Invalid format on line {line_number}: {line}")
    
    return {
        'host': parts[0],
        'port': parts[1],
        'username': parts[2],
        'password': parts[3]
    }


# Load credentials and proxy
creds = load_credentials(ACCOUNT_LINE)
proxy_info = load_proxy(ACCOUNT_LINE)

X_USERNAME = creds['x_username']
X_PASSWORD = creds['x_password']
OUTLOOK_EMAIL = creds['outlook_email']
OUTLOOK_PASSWORD = creds['outlook_password']

PROXY_HOST = proxy_info['host']
PROXY_PORT = proxy_info['port']
PROXY_USER = proxy_info['username']
PROXY_PASS = proxy_info['password']

# Global tab handles for confirmation code
outlook_tab_handle = None
x_tab_handle = None


def get_profile_dir(email):
    """Get unique profile directory for each account."""
    email_prefix = email.split('@')[0]
    profile_dir = os.path.join(SCRIPT_DIR, "profiles", email_prefix)
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir


def click_if_exists(driver, by, value, description="element", timeout=3):
    """Click element if it exists."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"[*] Found {description}, clicking...")
        element.click()
        return True
    except:
        return False


def login_outlook(driver, email, password):
    """Login to Outlook mail."""
    print("\n" + "=" * 50)
    print("STEP 1: Outlook Login")
    print("=" * 50)
    
    print("[*] Navigating to Outlook login page...")
    driver.get("https://outlook.live.com/mail/0/?prompt=select_account")
    time.sleep(3)
    
    # Enter email
    print(f"[*] Entering email: {email}")
    try:
        email_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        email_field.send_keys(email)
        email_field.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"[!] Error entering email: {e}")
        return False
    
    time.sleep(3)
    
    # Check for "Use your password" link
    if click_if_exists(driver, By.LINK_TEXT, "Use your password", "Use your password"):
        time.sleep(2)
    
    # Enter password
    print("[*] Waiting for password field...")
    try:
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        time.sleep(1)
        password_field.click()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Click Next/Sign in button
        print("[*] Clicking Sign in button...")
        click_if_exists(driver, By.ID, "idSIButton9", "Sign in button", 5)
        
    except Exception as e:
        print(f"[!] Error entering password: {e}")
        return False
    
    # Handle post-login prompts
    print("[*] Handling post-login prompts...")
    for _ in range(20):
        time.sleep(2)
        current_url = driver.current_url
        print(f"[*] Current URL: {current_url}")
        
        if "outlook.live.com/mail" in current_url and "prompt=" not in current_url:
            print("[+] Successfully reached Outlook inbox!")
            return True
        
        # Try various prompts
        click_if_exists(driver, By.LINK_TEXT, "Use your password", "Use your password")
        click_if_exists(driver, By.ID, "idBtn_Back", "No (Stay signed in)")
        click_if_exists(driver, By.LINK_TEXT, "Skip for now", "Skip for now")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Skip')]", "Skip")
        click_if_exists(driver, By.XPATH, "//a[contains(text(),'Skip')]", "Skip link")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Next')]", "Next")
        click_if_exists(driver, By.ID, "idSIButton9", "Next button")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'OK')]", "OK")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Yes')]", "Yes")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Continue')]", "Continue")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Done')]", "Done")
        click_if_exists(driver, By.XPATH, "//button[contains(text(),'Got it')]", "Got it")
    
    return False


def human_type(element, text, min_delay=0.08, max_delay=0.18):
    """Type text with human-like delays."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))


def get_confirmation_code_from_outlook(driver, outlook_tab, x_tab):
    """Switch to Outlook, find X confirmation email, extract code, return to X."""
    import re
    
    print("\n" + "=" * 50)
    print("GETTING CONFIRMATION CODE FROM OUTLOOK")
    print("=" * 50)
    
    # Switch to Outlook tab
    print("[*] Switching to Outlook inbox...")
    driver.switch_to.window(outlook_tab)
    time.sleep(2)
    
    # Refresh inbox to get new emails
    print("[*] Refreshing inbox...")
    driver.refresh()
    time.sleep(5)
    
    confirmation_code = None
    max_attempts = 2  # Only try 2 times, then manual
    
    for attempt in range(max_attempts):
        print(f"[*] Looking for X confirmation email... (attempt {attempt + 1}/{max_attempts})")
        
        try:
            # Look for email from X with "confirmation code" in title
            email_selectors = [
                "//span[contains(text(),'confirmation code')]",
                "//span[contains(text(),'Your X confirmation')]",
                "//span[contains(text(),'X confirmation code')]",
                "//div[contains(text(),'confirmation code')]",
            ]
            
            email_found = False
            for selector in email_selectors:
                try:
                    emails = driver.find_elements(By.XPATH, selector)
                    if emails:
                        print(f"[*] Found X confirmation email, clicking...")
                        emails[0].click()
                        time.sleep(3)
                        email_found = True
                        break
                except:
                    continue
            
            if not email_found:
                # Try clicking the first/newest email in inbox
                try:
                    # Click on first email item
                    first_email = driver.find_element(By.CSS_SELECTOR, '[role="option"]')
                    first_email.click()
                    time.sleep(3)
                    email_found = True
                except:
                    pass
            
            if email_found:
                # Try to extract alphanumeric code from email
                try:
                    # Get email body text
                    page_text = driver.find_element(By.TAG_NAME, 'body').text
                    print(f"[*] Searching for code in email...")
                    
                    # Pattern 1: "confirmation code is XXXXXXXX" (alphanumeric 8 chars)
                    code_match = re.search(r'confirmation code is\s+([a-z0-9]{8})', page_text, re.IGNORECASE)
                    if code_match:
                        confirmation_code = code_match.group(1)
                        print(f"[+] Found confirmation code: {confirmation_code}")
                        break
                    
                    # Pattern 2: Standalone 8-char alphanumeric code on its own line
                    code_match = re.search(r'\n([a-z0-9]{8})\n', page_text, re.IGNORECASE)
                    if code_match:
                        confirmation_code = code_match.group(1)
                        print(f"[+] Found confirmation code: {confirmation_code}")
                        break
                    
                    # Pattern 3: Any 8-char lowercase alphanumeric that looks like a code
                    code_match = re.search(r'\b([a-z][a-z0-9]{7})\b', page_text)
                    if code_match:
                        confirmation_code = code_match.group(1)
                        print(f"[+] Found confirmation code: {confirmation_code}")
                        break
                    
                    # Pattern 4: 6-digit numeric code (fallback)
                    code_match = re.search(r'\b(\d{6})\b', page_text)
                    if code_match:
                        confirmation_code = code_match.group(1)
                        print(f"[+] Found confirmation code: {confirmation_code}")
                        break
                        
                except Exception as e:
                    print(f"[!] Error reading email body: {e}")
            
            # If code not found, refresh and try again
            if not confirmation_code and attempt < max_attempts - 1:
                print("[*] Code not found, refreshing inbox...")
                driver.refresh()
                time.sleep(5)
                
        except Exception as e:
            print(f"[!] Error searching for email: {e}")
            time.sleep(3)
    
    # Switch back to X tab
    print("[*] Switching back to X tab...")
    driver.switch_to.window(x_tab)
    time.sleep(2)
    
    if not confirmation_code:
        print("[!] Could not find confirmation code after 2 attempts")
        print("[!] Please enter the code manually on X")
    
    return confirmation_code


def login_x(driver, email, password):
    """Login to X (Twitter) with credentials in a new tab."""
    global outlook_tab_handle, x_tab_handle  # Store for confirmation code retrieval
    
    print("\n" + "=" * 50)
    print("STEP 2: X (Twitter) Login")
    print("=" * 50)
    
    # Store original window handle (Outlook tab)
    outlook_tab_handle = driver.current_window_handle
    original_tabs = len(driver.window_handles)
    print(f"[*] Outlook tab stored")
    print(f"[*] Current tabs: {original_tabs}")
    
    # Open new tab using Selenium method
    print("[*] Opening new tab for X login...")
    
    # Use Ctrl+T to open new tab (works with Selenium)
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.CONTROL + 't')
    time.sleep(2)
    
    # Check if new tab opened
    if len(driver.window_handles) > original_tabs:
        # Switch to the new tab
        all_handles = driver.window_handles
        x_tab_handle = [h for h in all_handles if h != outlook_tab_handle][0]
        driver.switch_to.window(x_tab_handle)
        print(f"[*] Switched to new tab")
        driver.get("https://x.com/i/flow/login")
    else:
        # Fallback: Try execute_script
        print("[*] Trying alternative method...")
        driver.execute_script("window.open('');")
        time.sleep(1)
        if len(driver.window_handles) > original_tabs:
            all_handles = driver.window_handles
            x_tab_handle = [h for h in all_handles if h != outlook_tab_handle][0]
            driver.switch_to.window(x_tab_handle)
            driver.get("https://x.com/i/flow/login")
            print(f"[*] Switched to new tab")
        else:
            # Last fallback: navigate in same tab
            print("[!] Could not open new tab, navigating in same tab...")
            x_tab_handle = outlook_tab_handle  # Same tab
            driver.get("https://x.com/i/flow/login")
    
    time.sleep(5)
    
    # Enter email/username
    print(f"[*] Entering email: {email}")
    try:
        # Wait for username/email field
        email_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
        )
        time.sleep(random.uniform(1, 2))
        email_field.click()
        time.sleep(random.uniform(0.5, 1))
        human_type(email_field, email)
        time.sleep(random.uniform(1, 2))
        
        # Click Next button
        print("[*] Clicking Next button...")
        next_button = driver.find_element(By.XPATH, "//span[text()='Next']/ancestor::button")
        next_button.click()
        time.sleep(random.uniform(3, 5))
        
    except Exception as e:
        print(f"[!] Error entering email: {e}")
        return False
    
    # Check if verification needed (unusual activity - asks for username/phone)
    try:
        verify_field = driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
        if verify_field:
            print("[!] X is asking for verification (phone/username)")
            print("[!] Please complete verification manually, then script will continue...")
            # Wait for user to complete verification
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
    except:
        pass
    
    # Enter password
    print("[*] Waiting for password field...")
    try:
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        time.sleep(random.uniform(1, 2))
        password_field.click()
        time.sleep(random.uniform(0.5, 1))
        human_type(password_field, password)
        time.sleep(random.uniform(1, 2))
        
        # Click Login button
        print("[*] Clicking Login button...")
        login_button = driver.find_element(By.XPATH, "//span[text()='Log in']/ancestor::button")
        login_button.click()
        time.sleep(random.uniform(5, 7))
        
    except Exception as e:
        print(f"[!] Error entering password: {e}")
        return False
    
    # Check if login successful
    print("[*] Checking login status...")
    for i in range(15):
        time.sleep(2)
        current_url = driver.current_url
        print(f"[*] Current URL: {current_url}")
        
        if "x.com/home" in current_url:
            print("[+] X login successful!")
            handle_x_post_login_prompts(driver)
            return True
        
        # Check for confirmation code required
        try:
            code_text = driver.find_element(By.XPATH, "//*[contains(text(),'confirmation code')]")
            if code_text:
                print("[!] X requires confirmation code from email")
                
                # Get code from Outlook automatically
                confirmation_code = get_confirmation_code_from_outlook(
                    driver, outlook_tab_handle, x_tab_handle
                )
                
                if confirmation_code:
                    print(f"[*] Entering confirmation code: {confirmation_code}")
                    
                    # Find code input field
                    try:
                        code_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
                        )
                        code_input.click()
                        time.sleep(0.5)
                        human_type(code_input, confirmation_code)
                        time.sleep(1)
                        
                        # Click Next/Verify button
                        try:
                            next_btn = driver.find_element(By.XPATH, "//span[text()='Next']/ancestor::button")
                            next_btn.click()
                        except:
                            try:
                                verify_btn = driver.find_element(By.XPATH, "//span[text()='Verify']/ancestor::button")
                                verify_btn.click()
                            except:
                                code_input.send_keys(Keys.ENTER)
                        
                        time.sleep(5)
                        
                        if "x.com/home" in driver.current_url:
                            print("[+] X login successful after code entry!")
                            handle_x_post_login_prompts(driver)
                            return True
                            
                    except Exception as e:
                        print(f"[!] Error entering code: {e}")
                else:
                    print("[!] Could not get code automatically")
                    print("[!] Please enter code manually...")
                    WebDriverWait(driver, 180).until(
                        lambda d: "x.com/home" in d.current_url
                    )
                    print("[+] X login successful after manual code entry!")
                    handle_x_post_login_prompts(driver)
                    return True
        except:
            pass
        
        # Check for wrong password
        try:
            error = driver.find_element(By.XPATH, "//*[contains(text(),'Wrong password')]")
            if error:
                print("[!] Wrong password!")
                return False
        except:
            pass
    
    # Final check
    if "x.com/home" in driver.current_url:
        print("[+] X login successful!")
        handle_x_post_login_prompts(driver)
        return True
    
    print("[!] X login may have failed. Current URL:", driver.current_url)
    return False


def handle_x_post_login_prompts(driver):
    """Handle post-login prompts on X like 'Review your email' and 'Accept cookies'."""
    print("[*] Checking for post-login prompts...")
    
    for _ in range(5):
        time.sleep(2)
        
        # Handle "Review your email" - Click "Yes, that's correct"
        try:
            yes_correct = driver.find_element(By.XPATH, "//span[contains(text(),\"Yes, that's correct\")]/ancestor::button")
            print("[*] Found 'Review your email' prompt, clicking 'Yes, that's correct'...")
            yes_correct.click()
            time.sleep(2)
        except:
            pass
        
        # Handle "Accept all cookies"
        try:
            accept_cookies = driver.find_element(By.XPATH, "//span[contains(text(),'Accept all cookies')]/ancestor::button")
            print("[*] Found cookie prompt, clicking 'Accept all cookies'...")
            accept_cookies.click()
            time.sleep(2)
        except:
            pass
        
        # Alternative cookie button selector
        try:
            accept_cookies = driver.find_element(By.XPATH, "//div[contains(text(),'Accept all cookies')]")
            print("[*] Found cookie prompt, clicking 'Accept all cookies'...")
            accept_cookies.click()
            time.sleep(2)
        except:
            pass
        
        # Check if we're on home page now
        if "x.com/home" in driver.current_url:
            break
    
    print("[*] Post-login prompts handled")


def wait_for_x_login_and_get_cookies(driver, outlook_email):
    """Wait for X login to complete, then get cookies."""
    print("\n[*] Waiting for X login to complete...")
    
    max_wait = 300  # 5 minutes
    check_interval = 2
    waited = 0
    
    while waited < max_wait:
        current_url = driver.current_url
        
        # Check if on X and logged in
        if "x.com/home" in current_url or ("x.com" in current_url and "/flow/login" not in current_url and "/i/flow" not in current_url):
            print(f"\n[+] X login detected! URL: {current_url}")
            time.sleep(3)
            return get_x_cookies(driver, outlook_email)
        
        if waited % 10 == 0:
            print(f"[*] Still waiting... ({waited}s / {max_wait}s)")
        
        time.sleep(check_interval)
        waited += check_interval
    
    print("[!] Timeout waiting for X login")
    return None


def get_x_cookies(driver, outlook_email):
    """Extract X cookies and save to JSON file."""
    print("\n" + "=" * 50)
    print("STEP 3: Extracting X Cookies")
    print("=" * 50)
    
    # Get all cookies
    all_cookies = driver.get_cookies()
    
    # Filter X cookies
    x_cookies = [c for c in all_cookies if 'x.com' in c.get('domain', '') or 'twitter.com' in c.get('domain', '')]
    
    print(f"[*] Total cookies: {len(all_cookies)}")
    print(f"[*] X cookies: {len(x_cookies)}")
    
    # Important cookies
    important = ['auth_token', 'ct0', 'twid', 'kdt', 'guest_id']
    print("\n[*] Important X cookies:")
    for cookie in x_cookies:
        if cookie['name'] in important:
            value = cookie['value']
            print(f"    {cookie['name']}: {value[:40]}..." if len(value) > 40 else f"    {cookie['name']}: {value}")
    
    # Create cookies directory
    cookies_dir = os.path.join(SCRIPT_DIR, "cookies")
    os.makedirs(cookies_dir, exist_ok=True)
    
    # Save JSON file
    email_prefix = outlook_email.split('@')[0]
    json_file = os.path.join(cookies_dir, f"{email_prefix}.json")
    with open(json_file, 'w') as f:
        json.dump(x_cookies, f, indent=2)
    print(f"\n[+] Cookies saved: {json_file}")
    
    return x_cookies


def main():
    print("=" * 50)
    print("Outlook + X Login (undetected-chromedriver)")
    print("=" * 50)
    print(f"Outlook Email: {OUTLOOK_EMAIL}")
    print(f"X Username: {X_USERNAME}")
    print(f"Proxy: {PROXY_HOST}:{PROXY_PORT}")
    print("=" * 50)
    
    # Get profile directory
    profile_dir = get_profile_dir(OUTLOOK_EMAIL)
    print(f"[*] Profile directory: {profile_dir}")
    
    # Configure Chrome options
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--password-store=basic')
    # Force hardware acceleration / change WebGL renderer
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--enable-webgl')
    options.add_argument('--ignore-gpu-blocklist')
    
    # Create proxy auth extension
    proxy_auth_extension = create_proxy_auth_extension(
        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS
    )
    if proxy_auth_extension:
        options.add_extension(proxy_auth_extension)
    
    print("[*] Launching Chrome with undetected-chromedriver...")
    driver = uc.Chrome(options=options, version_main=None)
    
    # Inject stealth scripts BEFORE any navigation
    stealth_script = """
    // WebGL Spoofing - intercept getParameter
    const origGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return 'Intel Inc.';
        if (param === 37446) return 'Intel Iris OpenGL Engine';
        return origGetParameter.call(this, param);
    };
    
    if (typeof WebGL2RenderingContext !== 'undefined') {
        const origGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return origGetParameter2.call(this, param);
        };
    }
    
    // Also override the debug extension
    const getExtension = WebGLRenderingContext.prototype.getExtension;
    WebGLRenderingContext.prototype.getExtension = function(name) {
        const ext = getExtension.call(this, name);
        if (name === 'WEBGL_debug_renderer_info' && ext) {
            return {
                UNMASKED_VENDOR_WEBGL: 37445,
                UNMASKED_RENDERER_WEBGL: 37446
            };
        }
        return ext;
    };
    """
    
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_script})
        print("[*] Stealth scripts injected")
    except Exception as e:
        print(f"[!] CDP injection failed: {e}")
    
    # Navigate to blank page first to ensure script is active
    driver.get('about:blank')
    time.sleep(0.5)
    
    try:
        # Step 1: Login to Outlook
        outlook_success = login_outlook(driver, OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
        
        if outlook_success:
            time.sleep(2)
            
            # Step 2: Login to X automatically
            x_success = login_x(driver, OUTLOOK_EMAIL, X_PASSWORD)
            
            if x_success:
                # Step 3: Extract cookies
                time.sleep(3)
                cookies = get_x_cookies(driver, OUTLOOK_EMAIL)
                
                if cookies:
                    print("\n" + "=" * 50)
                    print("[+] ALL DONE!")
                    print(f"[+] Extracted {len(cookies)} X cookies")
                    print("=" * 50)
            else:
                print("\n[!] X login failed. You can try manually...")
                cookies = wait_for_x_login_and_get_cookies(driver, OUTLOOK_EMAIL)
                if cookies:
                    print("\n" + "=" * 50)
                    print("[+] ALL DONE!")
                    print(f"[+] Extracted {len(cookies)} X cookies")
                    print("=" * 50)
        
        print("\n[*] Browser will stay open. Press Ctrl+C to close.")
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n[*] Closing browser...")
    except Exception as e:
        print(f"[!] Error: {e}")
        print("\n[*] Browser will stay open. Press Ctrl+C to close.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass
    finally:
        driver.quit()


def create_proxy_auth_extension(host, port, username, password):
    """Create Chrome extension for proxy authentication."""
    import zipfile
    import tempfile
    
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """
    
    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{host}",
                port: parseInt({port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{username}",
                password: "{password}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """
    
    try:
        # Create temporary directory for extension
        ext_dir = tempfile.mkdtemp()
        ext_path = os.path.join(ext_dir, 'proxy_auth.zip')
        
        with zipfile.ZipFile(ext_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        
        return ext_path
    except Exception as e:
        print(f"[!] Could not create proxy auth extension: {e}")
        return None


if __name__ == "__main__":
    main()
