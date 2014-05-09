# coding: utf-8
import os
from flask import Flask, render_template, request, abort, redirect, url_for
from watchapp.extensions import db
from watchapp.models import File, Field, Metadata


app = Flask(__name__)
config = os.path.join(app.root_path, 'settings.py')
app.config.from_pyfile(config)
db.init_app(app)


@app.route('/')
def mainpage():
    """
    Show 20 recently updated Files
    """
    items = (
        File.query
        .filter(File.status == File.STATUS.NORMAL.db)
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
    """
    List all items deleted from the UI
    """
    items = (
        File.query
        .filter(File.status == File.STATUS.DELETED.db)
        .order_by(File.updated_at.desc())
        .all()
    )
    return render_template(
        'listing.html',
        active_menu='deleted',
        items=items
    )


@app.route('/items/<int:item_id>', methods=['GET'])
def view_item(item_id):
    """
    Show information about `File` with metadata.
    If file is Image, render it on the page.

    :param item_id: id of `File`
    """
    item = File.query.filter(File.id == item_id).first()
    if not item:
        abort(404)
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
    :param item_id: id of `File` to edd metadata

    form params:
    :param metafield: id of `Field` to add metadata to file
    :param metavalue: value of the metadata provided by user

    """

    field_id = request.form.get('metafield')
    value = request.form.get('metavalue')

    field = Field.query.filter(Field.id == field_id).first()
    fl = File.query.filter(File.id == item_id).first()
    if not (field and fl):
        abort(400)

    meta = Metadata()
    meta.file_id = fl.id
    meta.content = value
    meta.field_info = field
    db.session.add(meta)
    fl.meta.append(meta)
    db.session.commit()
    return redirect(url_for('view_item', item_id=item_id))


@app.route('/items/<int:item_id>/change_status', methods=['POST'])
def change_status(item_id):
    """
    Endpoint used for delete/recover files from UI
    :param item_id: id of `File` to change status
    """

    item = File.query.filter(File.id == item_id).first()
    status = request.form.get('status')
    if not (item and status):
        abort(404)
    item.status = int(status)
    db.session.commit()
    return redirect(url_for('mainpage'))


@app.route('/items', methods=['POST'])
def create_item():
    """
    Main endpoint to receive data from watchdog daemon
    form params:
    :param path: full path of file that was changed
    :param event_type: type of event happened to file, created/deleted etc
    :param type:

    """
    file_path = request.form.get('path')
    action_type = request.form.get('event_type')
    mimetype = request.form.get('type')

    if not (file_path and action_type):
        abort(400)

    fl = File.query.filter(File.path == file_path).first()
    if action_type == 'deleted':
        if fl:
            # if file exists in database and was deleted from FS
            # remove it and all its metadata from database
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


@app.route('/settings', methods=['GET'])
def settings():
    """
    Form for managing metadata fields,
    Just list all of available fields.

    :return:
    """
    fields = Field.query.all()
    return render_template(
        'settings.html',
        fields=fields
    )


@app.route('/settings/create', methods=['POST'])
def create_field():
    """
    Endpoint for different settings.
    Currently used only to create new types of metadata fields

    form params:
    :param fld_name: name for metadata field
    :param description: description of metadata field

    """
    name = request.form.get('fld_name')
    description = request.form.get('description')
    if not name:
        abort(404)

    field = Field()
    field.name = name
    field.description = description
    db.session.add(field)
    db.session.commit()
    return redirect(url_for('settings'))


@app.route('/search', methods=['GET'])
def search():
    """
    Endpoint to search files

    query params:
    :param q: search query
    :param scope: scope to search in, can be `filename` or `metadata`,
        default is `filename`
    """
    query = request.args.get('q')
    scope = request.args.get('scope', 'filename')
    results = []
    if not query:
        return redirect(url_for('mainpage'))

    if scope == 'metadata':
        ids = (
            db.session
            .query(Metadata.file_id)
            .join(File)
            .filter(Metadata.content.ilike('%{0}%'.format(query)))
            .filter(File.status == File.STATUS.NORMAL.db)
            .all()
        )
        if ids:
            results = (
                File.query
                .filter(File.id.in_(ids))
                .all()
            )
    else:
        results = (
            File.query
            .filter(File.filename.ilike('%{0}%'.format(query)))
            .filter(File.status == File.STATUS.NORMAL.db)
            .all()
        )

    title = u"Search results for term `{0}` in `{1}` scope".format(query, scope)

    return render_template(
        'listing.html',
        items=results,
        title=title
    )