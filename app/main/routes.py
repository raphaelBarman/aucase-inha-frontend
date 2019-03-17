from flask import render_template, request, abort
from app.main import bp
from flask import jsonify
import dateutil.parser as date_parse
from app.models import Actor, Object, Sale, Section, object2iiif

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Aucase')

@bp.route("/search", methods=['POST'])
def w_search():
    experts = set(request.json['experts'])
    commissaires = set(request.json['commissaires'])
    actors_first_names = [x.split('/')[0] for x in experts]
    actors_first_names += [x.split('/')[0] for x in commissaires]
    actors_last_names = [x.split('/')[1] for x in experts]
    actors_last_names += [x.split('/')[1] for x in commissaires]
    object_query = request.json['objectsearch']
    section_query = request.json['sectionsearch']
    start_date = request.json['startdate']
    end_date = request.json['enddate']
    page = request.args.get('page', 1, type=int)
    objects = Object.query
    if len(object_query) > 0:
        if not object_query.startswith('"') or not object_query.endswith('"'):
            object_query += '*'
        objects = objects.filter(Object.text.match(object_query))
    if len(section_query) > 0:
        if not section_query.startswith('"') or not section_query.endswith('"'):
            section_query += '*'
        objects = objects.filter(
            Object.parent_section.has(
                (Section.text.match(section_query)) |
                (Section.parent_section.has(Section.text.match(section_query)))
            ))
    if len(actors_last_names) > 0:
        objects = objects.filter(
            Object.sale.has(
                Sale.actors.any(
                    Actor.first_name.in_(actors_first_names) &
                    Actor.last_name.in_(actors_last_names))))
    if start_date:
        try:
            start_date = date_parse.parse(start_date)
            objects = objects.filter(Object.sale.has(Sale.date >= start_date))
        except:
            pass
    if end_date:
        try:
            end_date = date_parse.parse(end_date)
            objects = objects.filter(Object.sale.has(Sale.date <= end_date))
        except:
            pass
    objects = objects.paginate(page, 20, False)
    parent_sections = [o.get_parent_sections() for o in objects.items]
    iiif_urls = [object2iiif(o) for o in objects.items]
    res = {}
    res['html'] = render_template('object-results.html', objects=zip(parent_sections, iiif_urls, objects.items))
    return jsonify(res)


@bp.route("/api", methods=['POST'])
def w_api():
    if 'experts' in request.args:
        actors = Actor.query.filter(Actor.role.contains('Expert')).all()
        return jsonify([(a.first_name, a.last_name)
             for a in actors])
    if 'commissaires' in request.args:
        actors = Actor.query.filter(Actor.role.contains('Commissaire-priseur')).all()
        return jsonify([(a.first_name, a.last_name)
             for a in actors])

    abort(404)
