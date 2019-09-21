from flask import render_template, request, abort, Response, stream_with_context
import requests
from app.main import bp
from flask import jsonify
from app.models import Actor, Object, Sale, object2iiif
from .search import search

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@bp.route("/search", methods=['GET'])
def index():
    return render_template('index.html', title='Aucase')

@bp.route("/api", methods=['POST'])
def w_api():
    if 'search' in request.args:
        try:
            actors_ids = set(request.json['actors'])
            object_query = request.json['objectsearch']
            section_author_query = request.json['sectionauthorsearch']
            section_category_query = request.json['sectioncategorysearch']
            start_date = request.json['startdate']
            end_date = request.json['enddate']
            sort_order = request.json['sortingorder']
            page = request.json['page'] if 'page' in request.json else 1;
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
        iiif_urls = [object2iiif(o) for o in objects.items]
        res = {}
        res['html'] = render_template('object-results.html', results_count=results_count, objects=zip(parent_sections, iiif_urls, objects.items))
        res['results_count'] = results_count
        return jsonify(res)
    if 'experts' in request.args:
        actors = Actor.query.filter(Actor.role.contains('Expert')).all()
        return jsonify([
            {
                'id': a.id,
                'first_name': a.first_name,
                'last_name': a.last_name,
            }
            for a in actors])
    if 'commissaires' in request.args:
        actors = Actor.query.filter(Actor.role.contains('Commissaire-priseur')).all()
        return jsonify([
            {
                'id': a.id,
                'first_name': a.first_name,
                'last_name': a.last_name,
            }
            for a in actors])

    abort(404)

@bp.route("/cors/<path:url>", methods=['GET'])
def proxy_cors(url):
    r = requests.get(url, stream=True, params=request.args)
    response = Response(stream_with_context(r.iter_content()),
                        content_type=r.headers['content-type'],
                        status=r.status_code)
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response
