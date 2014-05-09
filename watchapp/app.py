# coding: utf-8
import os
from flask import Flask, render_template, request, abort, redirect, url_for
from watchapp.extensions import db
from watchapp.models import File, Field, Metadata


app = Flask(__name__)
config = os.path.join(app.root_path, 'settings.py')
app.config.from_pyfile(config)
db.init_app(app)


def get_status_by_title(title, default):
    for status in File.STATUS:
        if status.title == title:
            return status
    return default

@app.route('/')
def mainpage():
    items = (
        File.query
        .filter(File.status==File.STATUS.NORMAL.db)
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
        .filter(File.status == File.STATUS.DELETED.db)
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
    item = File.query.filter(File.id == item_id).first()
    if not item:
        return abort(404)
    fields = Field.query.limit(20).all()
    return render_template(
        'item_view.html',
        item=item,
        fields=fields
    )


@app.route('/items/<int:item_id>', methods=['POST'])
def update_item(item_id):
    """
    Attach metadata to file
    :param item_id:
    :return:
    """

    field_id = request.form.get('metafield')
    value = request.form.get('metavalue')

    field = Field.query.filter(Field.id == field_id).first()
    file = File.query.filter(File.id == item_id).first()
    if not (field and file):
        return abort(400)

    meta = Metadata()
    meta.file_id = file.id
    meta.content = value
    meta.field_info = field
    db.session.add(meta)
    file.meta.append(meta)
    db.session.commit()
    return redirect(url_for('view_item', item_id=item_id))


@app.route('/items/<int:item_id>/change_status', methods=['POST'])
def change_status(item_id):
    item = File.query.filter(File.id == item_id).first()
    status = request.form.get('status')
    if not (item and status):
        return abort(404)
    item.status = int(status)
    db.session.commit()
    return redirect(url_for('mainpage'))


@app.route('/items', methods=['POST'])
def create_item():
    file_path = request.form.get('path')
    action_type = request.form.get('event_type')
    mimetype = request.form.get('type')

    if not (file_path and action_type):
        abort(400)

    fl = File.query.filter(File.path == file_path).first()
    if get_status_by_title(action_type, None) == File.STATUS.DELETED and fl:
        db.session.delete(fl)
        db.session.commit()
        return 'ok'

    file_name = file_path.split('/')[-1]
    if not fl:
        fl = File()
    fl.filename = file_name
    fl.path = file_path
    fl.mimetype = mimetype
    fl.status = File.STATUS.NORMAL

    db.session.add(fl)
    db.session.commit()
    return 'ok'


@app.route('/settings')
def settings():
    """
    Form for managing metadata fields
    :return:
    """
    fields = Field.query.limit(20)
    if request.method == "POST":
        return ''
    return render_template(
        'settings.html',
        fields=fields
    )


@app.route('/settings/create', methods=['POST'])
def create_field():
    name = request.form.get('fld_name')
    description = request.form.get('description')
    if not name:
        return abort(404)

    field = Field()
    field.name = name
    field.description = description
    db.session.add(field)
    db.session.commit()
    return redirect(url_for('settings'))

