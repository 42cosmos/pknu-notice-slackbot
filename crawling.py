from selenium import webdriver

from selenium.webdriver.common.by import By
from dataclasses import dataclass

from slack_messanger import SlackMessenger


@dataclass
class NoticeRow:
    text: str
    update_date: str
    link_to_notice: str


def get_table_rows(row):
    text = row.find_element(By.CLASS_NAME, "bdlTitle")
    update_date = row.find_element(By.CLASS_NAME, "bdlDate")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")

    return NoticeRow(text.text, update_date.text, link_to_notice)


def main(driver, url):
    # driver.implicitly_wait(3)  # 묵시적 대기
    driver.get(url=url)

    board_table = driver.find_element(By.CLASS_NAME, "a_brdList")
    table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = table_body[0].find_elements(By.TAG_NAME, "tr")

    slack_message_list = []
    for row in rows:
        slack_message_list.append(get_table_rows(row))

    return slack_message_list


def make_slack_format(gradudate: bool, notice: NoticeRow) -> dict:
    school_name = "대학원" if gradudate else "학부"
    slack_text = {
        "title": notice.text,
        "title_link": notice.link_to_notice,
        "footer": f"{school_name}  |  {notice.update_date}",
    }

    return slack_text


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome("chromedriver_path", options=options)
    slack = SlackMessenger(test=False, key_path="sample_slack_key.json")

    # 대학원
    graduate_url = "https://sme.pknu.ac.kr/sme/1849"
    graduate_notice = main(driver, graduate_url)

    for notice in graduate_notice:
        slack.alarm_msg(make_slack_format(gradudate=True, notice=notice))

    # 학부
    undergraduate_url = "https://sme.pknu.ac.kr/sme/721"
    undergraduate_notice = main(driver, undergraduate_url)

    for notice in undergraduate_notice:
        slack.alarm_msg(make_slack_format(gradudate=False, notice=notice))