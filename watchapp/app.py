# coding: utf-8
import os
from flask import Flask, render_template, request, abort, redirect, url_for
from watchapp.extensions import db
from watchapp.models import File


app = Flask(__name__)
config = os.path.join(app.root_path, 'settings.py')
app.config.from_pyfile(config)
db.init_app(app)


STATUSES_MAPPING = {
    'created': File.STATUS_NORMAL,
    'modified': File.STATUS_NORMAL,
    'deleted': File.STATUS_MISSING
}

@app.route('/')
def mainpage():
    items = (
        File.query
        .filter(File.status==File.STATUS_NORMAL)
        .order_by(File.updated_at.desc())
        .limit(20)
        .all()
    )
    return render_template(
        'listing.html',
        active_menu='recent',
        items=items
    )

@app.route('/deleted')
def deleted():
    items = (
        File.query
        .filter(File.status==File.STATUS_DELETED)
        .order_by(File.updated_at.desc())
        .limit(20)
        .all()
    )
    return render_template(
        'listing.html',
        active_menu='deleted',
        items=items
    )


@app.route('/search')
def search():
    return render_template(
        'listing.html'
    )



@app.route('/items/<int:item_id>', methods=['GET'])
def view_item(item_id):
    item = File.query.filter(File.id==item_id).first()
    if not item:
        return abort(404)

    return render_template(
        'item_view.html',
        item=item
    )



@app.route('/items/<int:item_id>', methods=['POST'])
def update_item(item_id):
    return render_template(
        'item_edit.html'
    )

@app.route('/items/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item = File.query.filter(File.id==item_id).first()
    if not item:
        return abort(404)
    item.status = File.STATUS_DELETED
    db.session.commit()
    return redirect(url_for('mainpage'))


@app.route('/items', methods=['POST'])
def create_item():
    file_path = request.form.get('path')
    action_type = request.form.get('event_type')
    mimetype = request.form.get('type')

    if not file_path or not action_type:
        print file_path,action_type
        abort(400)

    file_name = file_path.split('/')[-1]
    fl = File.query.filter(File.path==file_path).first()
    if not fl:
        fl = File()
    fl.filename=file_name
    fl.path=file_path
    fl.mimetype=mimetype
    fl.status = STATUSES_MAPPING.get(action_type, File.STATUS_NORMAL)

    db.session.add(fl)
    db.session.commit()
    return 'ok'