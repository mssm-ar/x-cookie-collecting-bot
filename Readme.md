# X Cookie Extractor

Automated script to extract cookies from X (Twitter) accounts by logging in through Outlook.com first, then X.com using proxies.

## Features

- ✅ Automated Outlook.com login
- ✅ Automated X.com login via proxies
- ✅ Handles verification codes (manual input)
- ✅ Extracts and saves cookies in JSON and Netscape formats
- ✅ Supports multiple accounts and proxies
- ✅ Stealth mode to avoid detection

## Requirements

- Python 3.8+
- Playwright browser automation library

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## File Format

### Accounts File (`order7526436.txt`)
Format: `x_username:x_password:outlook_email:outlook_password`
```
username1:password1:email1@outlook.com:outlook_pass1
username2:password2:email2@outlook.com:outlook_pass2
```

### Proxies File (`Webshare 50 proxies.txt`)
Format: `ip:port:username:password`
```
1.2.3.4:8080:proxy_user:proxy_pass
5.6.7.8:9090:proxy_user2:proxy_pass2
```

## Usage

### Process all accounts:
```bash
python x_cookie_extractor.py
```

### Process a single account (by index):
```bash
python x_cookie_extractor.py --single 0
```

### Run in headless mode (no browser window):
```bash
python x_cookie_extractor.py --headless
```

### Custom delay between accounts:
```bash
python x_cookie_extractor.py --delay 10
```

### Custom file paths:
```bash
python x_cookie_extractor.py --accounts my_accounts.txt --proxies my_proxies.txt
```

## Command Line Options

- `--accounts`: Path to accounts file (default: `order7526436.txt`)
- `--proxies`: Path to proxies file (default: `Webshare 50 proxies.txt`)
- `--headless`: Run browser in headless mode
- `--single INDEX`: Process only account at specified index (0-based)
- `--delay SECONDS`: Delay between accounts in seconds (default: 5)

## Output

Cookies are saved in the `cookies/` directory:
- `{username}_cookies.json` - JSON format
- `{username}_cookies.txt` - Netscape format

## How It Works

1. **Outlook Login**: Script logs into Outlook.com with provided credentials
2. **Verification Handling**: If verification code is required, script will prompt for manual input
3. **X Login**: Script navigates to X.com and logs in using X credentials via proxy
4. **Cookie Extraction**: After successful login, cookies are extracted and saved

## Notes

- The script will pause and ask for verification codes when needed
- Each account uses a random proxy from the proxy list
- Browser runs in visible mode by default (use `--headless` for background operation)
- Cookies are saved immediately after successful login

## Troubleshooting

- **Login fails**: Check credentials and ensure accounts are not locked
- **Verification required**: Script will prompt - check your email/phone
- **Proxy errors**: Verify proxy credentials and connectivity
- **Timeout errors**: Increase delay between accounts or check network connection

