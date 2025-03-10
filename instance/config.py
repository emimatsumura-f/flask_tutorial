import os

# デフォルトの設定
SECRET_KEY = 'dev'  # セッション管理やその他のセキュリティ関連のニーズに使用される
DATABASE = os.path.join(os.path.dirname(__file__), 'flaskr.sqlite')  # SQLiteデータベースファイルへのパス
DEBUG = True  # デバッグモードを有効にする