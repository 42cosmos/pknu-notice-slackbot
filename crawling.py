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


def write_page_id_to_file(hrefs: list, db_file_name="page_id.txt"):
    append_type = "a" if os.path.exists(db_file_name) else "w"
    with open(db_file_name, append_type) as f:
        for page_id in hrefs:
            f.write(f"\n{page_id}")


def load_page_id_from_file(db_file_name="page_id.txt"):
    if os.path.exists(db_file_name) is False:
        return set()

    with open(db_file_name, "r") as f:
        page_id_list = set(f.read().strip().split())
        return page_id_list


def get_table_rows(row):
    text = row.find_element(By.CLASS_NAME, "bdlTitle")
    update_date = row.find_element(By.CLASS_NAME, "bdlDate")
    hyperlink = row.find_element(By.TAG_NAME, "a")
    link_to_notice = hyperlink.get_attribute("href")

    return NoticeRow(text.text, update_date.text, link_to_notice)


def set_driver(driver, url):
    # driver.implicitly_wait(3)  # 묵시적 대기
    driver.get(url=url)

    board_table = driver.find_element(By.CLASS_NAME, "a_brdList")
    table_body = board_table.find_elements(By.TAG_NAME, "tbody")
    rows = table_body[0].find_elements(By.TAG_NAME, "tr")

    slack_message_list = []
    for row in rows:
        slack_message_list.append(get_table_rows(row))

    return slack_message_list


def make_slack_format(graduate: bool, notice: NoticeRow) -> dict:
    school_name = "대학원" if graduate else "학부"
    slack_text = {
        "title": notice.text,
        "title_link": notice.link_to_notice,
        "footer": f"{school_name}  |  {notice.update_date}",
    }
    return slack_text


def send_slack_message(slack, notice, check_graduate, page_ids):
    if notice.link_to_notice not in page_ids:
        slack.alarm_msg(make_slack_format(graduate=check_graduate, notice=notice))
        return True
    return False


def process_notices(driver, slack, url, graduate, page_ids):
    notices = set_driver(driver, url)
    new_page_ids = []
    for notice in notices:
        sent = send_slack_message(slack=slack,
                                  notice=notice,
                                  check_graduate=graduate,
                                  page_ids=page_ids)
        if sent:
            new_page_ids.append(notice.link_to_notice)
    return new_page_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str, default="")
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    new_page_ids_to_write = []
    db_file = os.path.join(args.workspace, "page_id.txt")

    driver = webdriver.Chrome(os.path.join(args.workspace, "chromedriver"), options=options)
    slack = SlackMessenger(test=True, key_path=os.path.join(args.workspace, "slack_key.json"))
    page_ids = load_page_id_from_file(db_file_name=db_file)

    # 대학원
    graduate_url = "https://sme.pknu.ac.kr/sme/1849"
    sent_graduate_ids = process_notices(driver, slack, graduate_url, graduate=True, page_ids=page_ids)
    new_page_ids_to_write.extend(sent_graduate_ids)
    print(f"New Pages for graduate student --> {len(sent_graduate_ids)}")

    # 학부
    undergraduate_url = "https://sme.pknu.ac.kr/sme/721"
    sent_undergraduate_ids = process_notices(driver, slack, undergraduate_url, graduate=False, page_ids=page_ids)
    new_page_ids_to_write.extend(sent_undergraduate_ids)
    print(f"New Pages for Undergraduate student --> {len(sent_undergraduate_ids)}")

    write_page_id_to_file(new_page_ids_to_write, db_file_name=db_file)

    driver.quit()
