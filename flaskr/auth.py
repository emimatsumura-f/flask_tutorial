import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# Blueprintを作成し、認証関連のルートをまとめる
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ユーザー登録用のルート
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # フォームからユーザー名とパスワードを取得
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # ユーザー名とパスワードのバリデーション
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # ユーザー情報をデータベースに挿入
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # ユーザー名が既に存在する場合のエラーハンドリング
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

# ログイン用のルート
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # フォームからユーザー名とパスワードを取得
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# ログアウト用のルート
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ログインしているユーザーをリクエストごとにロードする関数
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# ログインが必要なルートを保護するデコレーター
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
