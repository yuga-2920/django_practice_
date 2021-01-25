from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidArgumentException
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import pandas as pd
import eel
import os
import time

class Jampepage:
    #パスワードの入力など
    def go_regration_page(self, driver, wait, password: str, id: str):
        url = "https://auctions.yahoo.co.jp/"
        driver.get(url)

        #ポップアップを削除
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Close-sc-rlasxu")))
            driver.execute_script('document.querySelector(".Close-sc-rlasxu.iYKltw").click()')

        except NoSuchElementException:
            pass

        #ログインページに移動
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "TextBold-sc-1u4qbnp")))
        driver.find_element_by_css_selector(".TextBold-sc-1u4qbnp.hxyLWa").find_element_by_tag_name("a").click()

        #ID/携帯電話/メールアドレスの入力
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        driver.find_element_by_id("username").send_keys(id)
        driver.find_element_by_id("btnNext").click()

        #パスワードの入力
        wait.until(EC.visibility_of_element_located((By.ID, "passwd")))
        driver.find_element_by_id("passwd").send_keys(password)
        driver.find_element_by_id("loginSubmit").find_element_by_id("btnSubmit").click()

    #商品の登録画面に移動
    def go_product_registration(self, driver, wait):
        product_registration_url = "https://auctions.yahoo.co.jp/jp/show/submit?category=0"
        driver.get(product_registration_url)

        #ポップアップの削除
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "CrossListingModal__close")))
            driver.execute_script('document.querySelector(".CrossListingModal__close").click()')

        except NoSuchElementException:
            pass

        except TimeoutException:
            pass

    #商品の出品
    def go_exhibits(self, driver, wait):
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Button--proceed")))
        button = driver.find_element_by_class_name("Button--proceed")
        button.click()

        try:
            wait.until(EC.visibility_of_element_located((By.ID, "OfficialModalNextBtn")))
            driver.execute_script('document.querySelector("#OfficialModalNextBtn").click()')
        
        except NoSuchElementException:
            pass

        except TimeoutException:
            pass
        
        wait.until(EC.visibility_of_element_located((By.ID, "auc_preview_submit_up")))
        button = driver.find_element_by_id('auc_preview_submit_up')
        button.click()

class Myscraipping:

    id_dict = {}

    #beautifulsoupの文字列の整形
    def string_format(self, text: str):
        text = text.replace(" ", "")
        text = text.replace(">", "")
        return text

    #カテゴリの取得
    def get_category(self, id: str):
        if id not in self.id_dict:
            url = "https://auctions.yahoo.co.jp/list/{}-category.html".format(id)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'lxml')
            yjBreadcrumbs = soup.find(attrs={"id": "yjBreadcrumbs"})
            if yjBreadcrumbs is not None:
                categorys_text = yjBreadcrumbs.get_text()
                categorys_split = self.string_format(categorys_text).splitlines()
                categorys = [category for category in categorys_split if category != '']
                categorys = categorys[2:]
                
                #idの登録
                self.id_dict[id] = categorys

                return categorys

        else:
            return self.id_dict[id]

    #ヤフネコ判定
    def delivery_yahuneko_method(self, driver, wait, nekoposu: str, nekotakkyu: str, nekotakkyukonpakuto: str):
        click_list = []
        wait.until(EC.visibility_of_element_located((By.ID, "yahunekoForm")))
        yahunekoform = driver.find_element_by_id("yahunekoForm")
        labels = yahunekoform.find_elements_by_tag_name("label")

        if nekoposu == "はい" and labels[0].get_attribute("class").find("is-check") < 0:
            click_list.append(labels[0])

        if nekotakkyu == "はい" and labels[1].get_attribute("class").find("is-check") < 0:
            click_list.append(labels[1])

        if nekotakkyukonpakuto == "はい" and labels[2].get_attribute("class").find("is-check") < 0:
            click_list.append(labels[2])

        return click_list

    #郵便判断
    def delivery_yubin_method(self, driver, wait, yupacket: str, yupack: str):
        click_list = []
        wait.until(EC.visibility_of_element_located((By.ID, "yubinForm")))
        yubinForm= driver.find_element_by_id("yubinForm")
        labels = yubinForm.find_elements_by_tag_name("label")

        if yupacket == "はい" and labels[0].get_attribute("class").find("is-check") < 0:
            click_list.append(labels[0])

        if yupack == "はい" and labels[0].get_attribute("class").find("is-check") < 0:
            click_list.append(labels[1])

        return click_list

    #その他の配送方法
    def delivery_other_method(self, driver, wait, item: str, num: int):
        wait.until(EC.visibility_of_element_located((By.ID, "auc_add_shipform")))
        elem = driver.find_element_by_id("auc_shipname_block{}".format(num))
        
        if elem.get_attribute("style") != "":
            #追加ボタンの選択
            driver.find_element_by_id("auc_add_shipform").click()
            wait.until(EC.visibility_of_element_located((By.ID, "auc_shipname_block{}".format(num))))

        label = elem.find_element_by_tag_name("label")
        if label.get_attribute("class").find("is-check") < 0:
            #ラベルの選択
            elem.click()
            wait.until(EC.visibility_of_element_located((By.ID, "auc_shipname_standard{}".format(num))))

        select = Select(driver.find_element_by_id("auc_shipname_standard{}".format(num)))
        select.select_by_value(item)
        
    #画像の登録
    def register_image(self, driver, wait, image_name: str):
        file = driver.find_element_by_id("selectFileMultiple")
        file_path = os.getcwd() + "/web/image/" + image_name
        file.send_keys(file_path)
        time.sleep(0.3)

    #商品名の登録
    def register_name(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.ID, "fleaTitleForm")))
        driver.find_element_by_id("fleaTitleForm").send_keys(text)

    #カテゴリの登録
    def register_category(self, driver, wait, id: str):
        category_list = self.get_category(id)
        if category_list:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "Category__button")))
            driver.find_element_by_class_name("Category__button").click()
            time.sleep(3)
            tab = driver.find_element_by_class_name("Tab")
            li = tab.find_elements_by_tag_name("li")[0]
            li.click()

            for i, category in enumerate(category_list):
                wait.until(EC.visibility_of_element_located((By.ID, "ptsSlctList{}".format(i))))
                ptsSlctList = driver.find_element_by_id("ptsSlctList{}".format(i))
                lis = ptsSlctList.find_elements_by_tag_name("li")
                for li in lis:
                    if li.text == category:
                        li.find_element_by_tag_name("a").click()
            else:
                wait.until(EC.visibility_of_element_located((By.ID, "updateCategory")))
                driver.find_element_by_id("updateCategory").click()

        else:
            eel.view_log_js("\n下記の商品のカテゴリは存在しません")

    #商品の状態
    def register_condition(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.NAME, "istatus")))
        select = Select(driver.find_element_by_name("istatus"))
        select.select_by_visible_text(text)

    #説明文
    def register_description(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.ID, "aucHTMLtag")))
        driver.find_element_by_id("aucHTMLtag").click()
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "descriptionArea__textArea")))
        driver.find_element_by_class_name("descriptionArea__textArea").send_keys(text)

    #発送元の地域
    def register_regions(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.NAME, "loc_cd")))
        select = Select(driver.find_element_by_name("loc_cd"))
        select.select_by_visible_text(text)

    #送料負担
    def register_shipping_cost(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.ID, "auc_shipping_who")))
        select = Select(driver.find_element_by_id("auc_shipping_who"))
        select.select_by_visible_text(text)

    #配送方法
    def register_delivery(self, driver, wait, nekoposu: str, nekotakkyu: str, nekotakkyukonpakuto: str, yupacket: str, yupack: str, item1: str, item2: str):
        yahuneko_click_list = self.delivery_yahuneko_method(driver, wait, nekoposu, nekotakkyu, nekotakkyukonpakuto)
        for click in yahuneko_click_list:
            click.click()

        yubin_click_list = self.delivery_yubin_method(driver, wait, yupacket, yupack)
        for click in yubin_click_list:
            click.click()
        
        self.delivery_other_method(driver, wait, item1, 1)
        self.delivery_other_method(driver, wait, item2, 2)

    #支払いから発送までの日数
    def register_day(self, driver, wait, text: str):
        wait.until(EC.visibility_of_element_located((By.NAME, "shipschedule")))
        select = Select(driver.find_element_by_name("shipschedule"))
        select.select_by_visible_text(text)

    #開始価格
    def register_price(self, driver, wait, price: str):
        wait.until(EC.visibility_of_element_located((By.ID, "auc_StartPrice_auction")))
        driver.find_element_by_id("auc_StartPrice_auction").send_keys(price)

    #終了する日時の設定
    def register_date_and_time(self, driver, wait, period: int, time: int):
        wait.until(EC.visibility_of_element_located((By.NAME, "ClosingYMD")))

        #終了する日にち
        today = date.today()
        end_day = today + timedelta(period)

        select = Select(driver.find_element_by_name("ClosingYMD"))
        select.select_by_value(str(end_day))

        #終了する時間
        select = Select(driver.find_element_by_name("ClosingTime"))
        select.select_by_value(str(time))


#ドライバーの設定
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



def main():

    #出品できなかった商品の格納
    not_register_item_list = [] 

    #csvファイルの読み込み
    df = pd.read_csv("./" + eel.csv_file()(), encoding="shift-jis")
    category_list = df["カテゴリ"].tolist()
    title_list = df["タイトル"].tolist()
    explain_list = df["説明"].tolist()
    price_list = df["開始価格"].tolist()
    period_list = df["開催期間"].tolist()
    end_time_list = df["終了時間"].tolist()
    image1_list = df["画像1"].tolist()
    image2_list = df["画像2"].tolist()
    image3_list = df["画像3"].tolist()
    image4_list = df["画像4"].tolist()
    image5_list = df["画像5"].tolist()
    image6_list = df["画像6"].tolist()
    image7_list = df["画像7"].tolist()
    image8_list = df["画像8"].tolist()
    image9_list = df["画像9"].tolist()
    image10_list = df["画像10"].tolist()
    sender_list = df["商品発送元の都道府県"].tolist()
    shipping_list = df["送料負担"].tolist()
    codition_list = df["商品の状態"].tolist()
    nekoposu_list = df["ネコポス"].tolist()
    nekotakkyukonpakuto_list = df["ネコ宅急便コンパクト"].tolist()
    nekotakkyu_list = df["ネコ宅急便"].tolist()
    yupaket_list = df["ゆうパケット"].tolist()
    yupaku_list = df["ゆうパック"].tolist()
    shipping_time_list = df["発送までの日数"].tolist()
    shipping1_list = df["配送方法1"].tolist()
    shipping2_list = df["配送方法2"].tolist()

    #クラスとwaitの定義
    jampepage = Jampepage()
    myscraipping = Myscraipping()

    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", True)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", True)

    wait = WebDriverWait(driver, 3)

    try:
        #ログイン
        jampepage.go_regration_page(driver, wait, eel.password()(), eel.id()())

    except Exception:
        eel.view_log_js("\nログインできませんでした。")

    #商品の出品
    for i in range(len(title_list)):
        try:
            if i % 100 == 0 and i != 0:
                driver.quit()
                if os.name == 'nt': #Windows
                    driver = set_driver("chromedriver.exe", True)
                elif os.name == 'posix': #Mac
                    driver = set_driver("chromedriver", True)

                wait = WebDriverWait(driver, 3)
                jampepage.go_regration_page(driver, wait, eel.password()(), eel.id()())

            jampepage.go_product_registration(driver, wait)
            try:
                myscraipping.register_image(driver, wait, image1_list[i])
                if image2_list[i] == image2_list[i]:
                    myscraipping.register_image(driver, wait, image2_list[i])
                    if image3_list[i] == image3_list[i]:
                        myscraipping.register_image(driver, wait, image3_list[i])
                        if image4_list[i] == image4_list[i]:
                            myscraipping.register_image(driver, wait, image4_list[i])
                            if image5_list[i] == image5_list[i]:
                                myscraipping.register_image(driver, wait, image5_list[i])
                                if image6_list[i] == image6_list[i]:
                                    myscraipping.register_image(driver, wait, image6_list[i])
                                    if image7_list[i] == image7_list[i]:
                                        myscraipping.register_image(driver, wait, image7_list[i])
                                        if image8_list[i] == image8_list[i]:
                                            myscraipping.register_image(driver, wait, image8_list[i])
                                            if image9_list[i] == image9_list[i]:
                                                myscraipping.register_image(driver, wait, image9_list[i])
                                                if image10_list[i] == image10_list[i]:
                                                    myscraipping.register_image(driver, wait, image10_list[i])
            
            except InvalidArgumentException:
                eel.view_log_js(str(i + 1) + "番目の画像が存在しません")
                continue

            myscraipping.register_name(driver, wait, title_list[i])
            myscraipping.register_category(driver, wait, category_list[i])
            myscraipping.register_condition(driver, wait, codition_list[i])
            myscraipping.register_description(driver, wait, explain_list[i])
            myscraipping.register_regions(driver, wait, sender_list[i])
            myscraipping.register_shipping_cost(driver, wait, shipping_list[i])
            myscraipping.register_delivery(driver, wait, nekoposu_list[i], nekotakkyukonpakuto_list[i], nekotakkyu_list[i], yupaket_list[i], yupaku_list[i], shipping1_list[i], shipping2_list[i])
            myscraipping.register_day(driver, wait, shipping_time_list[i])
            myscraipping.register_price(driver, wait, price_list[i])
            myscraipping.register_date_and_time(driver, wait, period_list[i], end_time_list[i])

            try:
                jampepage.go_exhibits(driver, wait)
                eel.view_log_js(str(i + 1) + "/" + str(len(title_list)) + " " + title_list[i] + "は出品できました")

            except NoSuchElementException:
                not_register_item_list.append(title_list[i])
                eel.view_log_js(str(i + 1) + "/" + str(len(title_list)) + " " + title_list[i] + "は出品できませんでした")

            except TimeoutException:
                not_register_item_list.append(title_list[i])
                eel.view_log_js(str(i + 1) + "/" + str(len(title_list)) + " " + title_list[i] + "は出品できませんでした")

        except TimeoutException:
                not_register_item_list.append(title_list[i])
                eel.view_log_js(str(i + 1) + "/" + str(len(title_list)) + " " + title_list[i] + "は出品できませんでした")

    else:
        result = pd.DataFrame({"出品できなかった商品": not_register_item_list})
        result.to_csv("出品できなかった商品.csv", encoding="utf-8_sig")

        eel.view_log_js("\n終了しました")
