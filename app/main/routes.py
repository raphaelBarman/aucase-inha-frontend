from flask import render_template, request
from app.main import bp
from app.models import Actor, Object


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    actor = Actor.query.all()[1]
    page = request.args.get('page', 1, type=int)
    objects = Object.query.paginate(page, 20, False)
    parent_sections = [o.get_parent_sections() for o in objects.items]
    return render_template('index.html', title='Aucase', actor=actor, objects=zip(parent_sections, objects.items))

@bp.route("/search")
def w_search():
    actor = Actor.query.all()[1]
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword')
    #results = Object.query.msearch(keyword,fields=['text']).paginate(page, 20, False)
    #results = Object.query.filter(FullTextSearch(keyword, Object)).paginate(page, 20, False)
    parent_sections = [o.get_parent_sections() for o in results.items]
    return render_template('index.html', title='Aucase', actor=actor, objects=zip(parent_sections, results.items))
