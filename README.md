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
Rename it to slack_key.json

You can ignore TEST_SLACK, but you have to set `test=False` in crawling.py file
1. WEB_HOOK_URL
2. Slack Channel ID you want to send message
3. ACCESSED TOKEN starts with xoxb

### 3. Download ChromeDriver
you can download chromedriver [here](https://chromedriver.chromium.org).
Be careful to download the same version of your chrome browser

PLACE ALL FILES IN THE SAME DIRECTORY ! 

### 4. RUN ! 
```python
python crawling.py --workspace <your path>
```

