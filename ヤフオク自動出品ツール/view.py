import eel
import sys
import desktop
import rakuma_automatic_exhibit

app_name="web/html"
end_point="index.html"
size=(500,450)

@ eel.expose
def main():
    try:
        rakuma_automatic_exhibit.main()
        sys.exit(0)

    except FileNotFoundError:
        eel.view_log_js("\nその名前のcsvファイルは存在しません")
        sys.exit(0)

    # except Exception:
    #     eel.view_log_js("\nエラーが生じました。この画面を閉じ最初からやり直してください")
    #     sys.exit(0)

desktop.start(app_name,end_point,size)
sys.exit(0)