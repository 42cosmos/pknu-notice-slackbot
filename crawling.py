import os.path

from selenium import webdriver

from selenium.webdriver.common.by import By
from dataclasses import dataclass

from slack_messanger import SlackMessenger
import argparse


@dataclass
class NoticeRow:
    text: str
    update_date: str
    link_to_notice: str


def write_page_id_to_file(href: str, db_file_name="page_id.txt"):
    if os.path.exists(db_file_name) is False:
        with open(db_file_name, "w") as f:
            f.write(f"\n{href}")
        return

    with open(db_file_name, "a") as f:
        f.write(f"\n{href}")


def load_page_id_from_file(href: str, db_file_name="page_id.txt"):
    if os.path.exists(db_file_name) is False:
        return set()

    with open("./page_id.txt", "r") as f:
        page_id_list = set(f.read().strip().split())
        return page_id_list


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


def send_slack_message(slack, notice, gradudate, page_ids, db_file_path):
    if notice.link_to_notice not in page_ids:
        slack.alarm_msg(make_slack_format(gradudate=gradudate, notice=notice))
        write_page_id_to_file(notice.link_to_notice, db_file_name=db_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str, default="")
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(os.path.join(args.workspace, "chromedriver"), options=options)
    slack = SlackMessenger(test=True, key_path=os.path.join(args.workspace, "slack_key.json"))

    # 대학원
    graduate_url = "https://sme.pknu.ac.kr/sme/1849"
    graduate_notice = main(driver, graduate_url)

    page_ids = load_page_id_from_file(graduate_url, db_file_name=os.path.join(args.workspace, "page_id.txt"))

    for notice in graduate_notice:
        send_slack_message(slack, notice, gradudate=True, page_ids=page_ids,
                           db_file_path=os.path.join(args.workspace, "page_id.txt"))

    # 학부
    undergraduate_url = "https://sme.pknu.ac.kr/sme/721"
    undergraduate_notice = main(driver, undergraduate_url)

    for notice in undergraduate_notice:
        send_slack_message(slack, notice, gradudate=False, page_ids=page_ids,
                           db_file_path=os.path.join(args.workspace, "page_id.txt")
