import dash
import dash_html_components as html
from sqlalchemy.orm import aliased
from sqlalchemy import func, text

def add_dash(server):
    app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix='/dash/'
    )

    from app.models import Actor, Section, Object, Sale, Actor_Sale
    from app import db
    with server.app_context():
        actor1 = aliased(Actor)
        actor2 = aliased(Actor)
        sale1 = aliased(Actor_Sale)
        sale2 = aliased(Actor_Sale)
        app.layout = html.Div([
            #str(db.session.query(Actor.first_name, Actor.last_name, func.count(Actor.id)).join(Sale, Actor.sales).join(Object, Sale.sale_objects).group_by(Actor.id).all()),
            str(db.session.query(actor1, actor2, func.count(actor1.id).label("total")).join(sale1, actor1.id == sale1.actor_id).join(sale2, sale2.sale_id==sale1.sale_id).join(actor2, actor2.id==sale2.actor_id).filter(actor1.id != actor2.id).group_by(actor1.id, actor2.id).order_by(text('total DESC')).all())
        ])

