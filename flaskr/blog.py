from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
# Flaskから必要なモジュールをインポート

# HTTPエラーを発生させるためのモジュールをインポート

# 認証が必要なルートを定義するためのデコレーターをインポート

# データベース接続を取得するための関数をインポート

bp = Blueprint('blog', __name__)
# ブループリントを作成。'blog'はブループリントの名前、__name__はモジュール名

@bp.route('/')
def index():
    db = get_db()
    # データベース接続を取得

    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    # 投稿を取得し、作成日時の降順で並べ替え

    return render_template('blog/index.html', posts=posts)
    # テンプレートに投稿を渡してレンダリング

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # 新規投稿作成のルート。GETとPOSTメソッドを許可
    if request.method == 'POST':
        # POSTリクエストの場合、フォームデータを取得
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            # タイトルが空の場合、エラーメッセージを設定
            error = 'Title is required.'

        if error is not None:
            # エラーがある場合、フラッシュメッセージを表示
            flash(error)
        else:
            # エラーがない場合、データベースに新規投稿を挿入
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            # 投稿後、ブログのインデックスページにリダイレクト
            return redirect(url_for('blog.index'))

    # GETリクエストの場合、投稿作成ページをレンダリング
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    # 指定されたIDの投稿を取得する関数
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        # 投稿が存在しない場合、404エラーを発生
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        # 投稿の著者が現在のユーザーでない場合、403エラーを発生
        abort(403)

    # 投稿を返す
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # 投稿の更新ルート。GETとPOSTメソッドを許可
    post = get_post(id)
    # 指定されたIDの投稿を取得

    if request.method == 'POST':
        # POSTリクエストの場合、フォームデータを取得
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            # タイトルが空の場合、エラーメッセージを設定
            error = 'Title is required.'

        if error is not None:
            # エラーがある場合、フラッシュメッセージを表示
            flash(error)
        else:
            # エラーがない場合、データベースの投稿を更新
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # 更新後、ブログのインデックスページにリダイレクト
            return redirect(url_for('blog.index'))

    # GETリクエストの場合、投稿更新ページをレンダリング
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # 投稿の削除ルート。POSTメソッドを許可
    get_post(id)
    # 指定されたIDの投稿を取得

    db = get_db()
    # データベース接続を取得

    db.execute('DELETE FROM post WHERE id = ?', (id,))
    # 指定されたIDの投稿を削除

    db.commit()
    # 変更をコミット

    # 削除後、ブログのインデックスページにリダイレクト
    return redirect(url_for('blog.index'))
