import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import numpy as np
import chromedriver_binary

# Chromeを起動する関数

def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

# main処理


def main():
    pg_counter = 1
    search_keyword = input("任意のキーワードを入力：")
    # driverを起動
    if os.name == 'nt': #Windows
        driver = Chrome("\\Program Files\\chromedriver\\chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = Chrome("\\Program Files\\chromedriver\\chromedriver.exe", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    while True:
        # ページ終了まで繰り返し取得
        exp_name_list = []
        # 検索結果の一番上の会社名を取得
        name_list = driver.find_elements_by_class_name("cassetteRecruit__name")

        #給与を取得
        exp_salary_list = []
        work_table_items = driver.find_elements_by_class_name("tableCondition")
        for item in work_table_items:
            salary = item.find_elements_by_tag_name("td")[3]
            exp_salary_list.append(salary.text)

        #掲載終了予定日の取得
        exp_end_date_list = []
        end_dates = driver.find_elements_by_class_name("cassetteRecruit__endDate")

        # 1ページ分繰り返し
        print(f"現在{pg_counter}件目")
        print(len(name_list))
        for name, salary, end_date in zip(name_list, exp_salary_list, end_dates):
            exp_name_list.append(name.text)
            exp_end_date_list.append(end_date.text[9:])
            # print("会社名：", name.text)
            # print("給与：", salary.text[9:])
            # print("掲載終了日：", end_date.text)
            # print("________________________________________________________________")

        #print("*****************************************************************************************************")

        time.sleep(5)

        try:
            next_page = driver.find_element_by_class_name("iconFont--arrowLeft")
            driver.execute_script("arguments[0].click();", next_page)
            pg_counter += 1

        except NoSuchElementException:
            exp_name_array = np.array(exp_name_list)
            exp_salary_array = np.array(exp_salary_list)
            exp_end_date_array = np.array(exp_end_date_list)
            result = pd.DataFrame({"会社名": exp_name_array, "給与": exp_salary_array, "掲載終了日": exp_end_date_array}) 
            result.to_csv(f"result_of_{search_keyword}.csv", index=False)
            print("NoSuchElementException")
            print("Finish")
            break

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
