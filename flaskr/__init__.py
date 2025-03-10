import os
from flask import Flask
from . import db
from . import auth
from . import blog

def create_app(test_config=None):
    # Flaskアプリケーションのインスタンスを作成
    app = Flask(__name__, instance_relative_config=True)
    # デフォルトの設定を構成
    app.config.from_mapping(
        SECRET_KEY='dev',  # セキュリティキー
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),  # データベースのパス
    )

    # テスト設定が渡された場合、それを使用
    if test_config is None:
        # インスタンスフォルダ内のconfig.pyから設定を読み込む
        app.config.from_pyfile('config.py', silent=True)
    else:
        # テスト設定を使用
        app.config.from_mapping(test_config)

    # インスタンスフォルダを作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # /hello ルートを定義
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # データベース関連の初期化
    db.init_app(app)

    # 認証関連のブループリントを登録
    app.register_blueprint(auth.bp)

    # ブログ関連のブループリントを登録
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
