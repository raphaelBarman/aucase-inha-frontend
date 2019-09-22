from flask import render_template, request, abort, Response, stream_with_context
import requests
from app.main import bp
from flask import jsonify
from app.models import Actor, Object, Sale
from .search import search


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Aucase')


@bp.route("/search", methods=['GET'])
def search_page():
    return render_template('search.html', title='Aucase')

@bp.route("/api", methods=['POST'])
def w_api():
    if 'search' in request.args:
        return handle_search(request)
    elif 'experts' in request.args:
        return export_actors('Expert')
    elif 'commissaires' in request.args:
        return export_actors('Commissaire-priseur')
    else:
        abort(404)


def handle_search(request):
    print(request.json)
    try:
        query = request.json
        actors_ids = set(query['actors'])
        object_query = query['objectsearch']
        section_author_query = query['sectionauthorsearch']
        section_category_query = query['sectioncategorysearch']
        start_date = query['startdate']
        end_date = query['enddate']
        sort_order = query['sortingorder']
        page = query['page'] if 'page' in request.json else 1;
    except:
        abort(500)
        
    objects = search(actors_ids, object_query,
                     section_author_query, section_category_query,
                     start_date, end_date)

    results_count = objects.count()
    if sort_order == 'date':
        objects = objects.join(Object.sale).order_by(Sale.date)
    objects = objects.paginate(page, 20, False)
    parent_sections = [o.get_parent_sections() for o in objects.items]
    res = {}
    res['html'] = render_template('object-results.html', results_count=results_count, objects=zip(parent_sections, objects.items))
    res['results_count'] = results_count
    return jsonify(res)


def export_actors(role):
    actors = Actor.query.filter(Actor.role.contains(role)).all()
    return jsonify([
        {
            'id': a.id,
            'first_name': a.first_name,
            'last_name': a.last_name,
        }
        for a in actors])
