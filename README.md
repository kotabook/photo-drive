# world-clock

当フォルダの"photo-drive"は、画像ファイルをアップロードして保存ができる、「Google Drive」の画像専用のようなものです。
* TOP画面
![photo](https://user-images.githubusercontent.com/104336680/170180242-e6892aff-a61b-4545-9f78-d39d5b3b58de.png)
* HOME画面
![upload](https://user-images.githubusercontent.com/104336680/170180270-9e5a23d2-bbb7-4309-b19b-cb7c801e4093.png)
* UPLOAD画面
![top](https://user-images.githubusercontent.com/104336680/170180279-505bc6f4-f60e-4d4f-86fb-881afe3ede01.png)

# Usage

1. `python manage.py makemigrations`を実行
2. `python manage.py migrate`を実行
3. `python manage.py runserver`を実行し、ターミナルに表示されるリンクにアクセスする

# Note
 
`config`フォルダの中にある`setting.py`の`SECRET_KEY`とメールアドレス送信のための必要事項はご自身で設定していただく必要があります。

メールアドレスの設定には以下のサイトを参考にさせていただきました。
https://freeheroblog.com/authenticationerror/
 
# License
 
ライセンスはありません。
自由にコピーして利用していただいて問題ありません。

# Contact
mail: kota03u2024@gmail.com
