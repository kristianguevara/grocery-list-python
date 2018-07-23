from flask import Flask, render_template, url_for, request, flash
import db, os

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

def create_app(test_config=None):

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    db.init_app(app)

    return app

db.init_app(app)

@app.route('/')
def index():
    dbo = db.get_db()
    items = dbo.execute(
        'SELECT * FROM list'
    ).fetchall()
    return render_template('index.html', items=items)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    if request.method == 'GET':
        dbo = db.get_db()
        item = dbo.execute(
            'SELECT * FROM list WHERE id = ?', (id,)
        ).fetchone()
        return render_template('edit.html', item=item)

    elif request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        dbo = db.get_db()
        error = None

        if not item_name or not description or not amount or not category:
            error = 'You have incomplete fields. Kindly double-check.'

        if error is None:
            dbo.execute(
                'UPDATE list SET item_name = ?, description = ?, amount = ?, category = ? WHERE id = ?',
                (item_name, description, amount, category, id)
            )
            dbo.commit()

            item = dbo.execute(
                'SELECT * FROM list WHERE id = ?', (id,)
            ).fetchone()
            flash('Successfully updated item!')
            return render_template('edit.html', item=item)
        else:
            flash(error)
            return render_template('edit.html', item=item)

@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete(id):
    if request.method == 'GET':
        dbo = db.get_db()
        item = dbo.execute(
            'SELECT * FROM list WHERE id = ?', (id,)
        ).fetchone()
        return render_template('delete.html', item=item)

    elif request.method == 'POST':
        dbo = db.get_db()
        error = None

        if not id:
            error = 'Item does no exist.'

        if error is None:
            dbo.execute(
                'DELETE from list WHERE id = ?',
                (id,)
            )
            dbo.commit()

            items = dbo.execute(
                'SELECT * FROM list'
            ).fetchall()

            return render_template('index.html', items=items)
        else:
            item = dbo.execute(
                'SELECT * FROM list WHERE id = ?', (id,)
            ).fetchone()
            flash(error)
            return render_template('delete.html', item=item)

@app.route('/add', methods=('GET', 'POST'))
def add():

    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        dbo = db.get_db()
        error = None

        if not item_name or not description or not amount or not category:
            error = 'You have incomplete fields. Kindly double-check.'

        if error is None:
            dbo.execute(
                'INSERT INTO list (item_name, description, amount, category) VALUES (?, ?, ?, ?)',
                (item_name, description, amount, category)
            )
            dbo.commit()
            flash('Successfully added an item!')
            return render_template('add.html')

        flash(error)

    return render_template('add.html')
