# X Cookie Extractor

Automated script to extract cookies from X (Twitter) accounts by logging in through Outlook.com first, then X.com using proxies.

## Features

- ✅ Automated Outlook.com login
- ✅ Manual X.com login with cookie extraction
- ✅ Proxy support with auto-authentication
- ✅ Anti-bot detection using undetected-chromedriver
- ✅ Separate Chrome profiles for each account
- ✅ Saves cookies in JSON format
- ✅ WebGL fingerprint spoofing

## System Requirements

- Python 3.8+
- Google Chrome browser
- Linux (tested on Ubuntu)

## Installation

### 1. Install system dependencies (sudo required):

```bash
# Install Google Chrome (if not installed)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Install xdotool (optional, for proxy auth backup)
sudo apt install xdotool
```

### 2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## File Format

### Credentials File (`x_credentials.txt`)
Format: `x_username:x_password:outlook_email:outlook_password`
```
username1:password1:email1@outlook.com:outlook_pass1
username2:password2:email2@outlook.com:outlook_pass2
```

### Proxies File (`proxy_list.txt`)
Format: `host:port:username:password`
```
1.2.3.4:8080:proxy_user:proxy_pass
5.6.7.8:9090:proxy_user:proxy_pass
```

## Configuration

Edit `x.py` to change the account line number:

```python
# ===========================================
# CONFIGURATION - Change line number here
# ===========================================
ACCOUNT_LINE = 1  # Which line to use (1 = first line)
# ===========================================
```

## Usage

### Run the script:
```bash
python3 x.py
```

### What happens:
1. **Chrome launches** with proxy configured
2. **Proxy auth dialog** appears → credentials filled automatically
3. **Outlook login** → automatic
4. **X login** → manual (to avoid bot detection)
5. **Cookies extracted** → saved to `cookies/` folder

## Output

Cookies are saved in the `cookies/` directory:
- `{outlook_email_prefix}.json` - JSON format

Example: `myemail.json` for `myemail@outlook.com`

## Directory Structure

```
x_cookie/
├── x.py                 # Main script
├── x_credentials.txt    # Account credentials
├── proxy_list.txt       # Proxy list
├── requirements.txt     # Python dependencies
├── cookies/             # Extracted cookies (auto-created)
│   └── {email}.json
└── profiles/            # Chrome profiles (auto-created)
    └── {email}/
```

## How It Works

1. **Outlook Login**: Script logs into Outlook.com automatically
2. **Post-login Handling**: Automatically handles "Stay signed in?", "Skip recovery", "Next" prompts
3. **X Login**: Script waits for manual X login (to avoid bot detection)
4. **Cookie Extraction**: After detecting successful X login, cookies are extracted and saved

## Troubleshooting

### Proxy auth dialog keeps appearing
- Make sure Chrome window has focus when dialog appears
- Credentials are auto-filled after 3 seconds

### X detects automation
- Login manually when prompted
- The script uses undetected-chromedriver to minimize detection

### WebGL Renderer shows SwiftShader
- This is normal on systems without GPU
- Script injects spoofing to hide this from websites

### "Could not log you in" on X
- Try a different proxy (change `ACCOUNT_LINE`)
- Wait a few minutes and try again
- The IP might be flagged by X

## Anti-Bot Features

- **undetected-chromedriver**: Patches Chrome to avoid Selenium detection
- **WebGL spoofing**: Hides software renderer fingerprint
- **Persistent profiles**: Each account gets its own Chrome profile
- **Human-like input**: Typing delays and mouse movements

## Notes

- Browser stays open after script completes (Ctrl+C to close)
- Each account should use a different proxy line
- First run may take longer as Chrome profile is created
- X login is manual to avoid bot detection - script only extracts cookies
