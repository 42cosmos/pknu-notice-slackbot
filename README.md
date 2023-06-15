# pknu-notice-slackbot

## requirements
- python 3.9
- selenium
- slack-sdk

## Usage

### 1. Install requirements
```bash
pip install -r requirements.txt
```

### 2. Set slackbot token in sample_slack_key.json
Rename it if you want to

You can ignore test parameter, but you have to set `test=False` in main file
1. WEB_HOOK_URL
2. Slack Channel ID you want to send message
3. ACCESSED TOKEN starts with xoxb

### 3. Download ChromeDriver
you can download chromedriver [here](https://chromedriver.chromium.org).
Be careful to download the same version of your chrome browser

### 4. Set keypath for SlackMessanger
```python
# crawling.py 
# line 55-56
driver = webdriver.Chrome("your_chromedriver_path", options=options)
slack = SlackMessenger(test=False, key_path="your_key_path")
```

