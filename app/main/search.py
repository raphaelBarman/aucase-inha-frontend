import dateutil.parser as date_parse
from app.models import Actor, Object, Sale, Section, object2iiif

def search(actors_ids,
           object_query,
           section_author_query,
           section_category_query,
           start_date,
           end_date):
    objects = Object.query
    if len(object_query) > 0:
        if not object_query.startswith('"') or not object_query.endswith('"'):
            object_query += '*'
        objects = objects.filter(Object.text.match(object_query))
    if len(section_author_query) > 0:
        if not section_author_query.startswith('"') or not section_author_query.endswith('"'):
            section_author_query += '*'
        objects = objects.filter(
            Object.parent_section.has(
                (Section.text.match(section_author_query) & Section._class.in_(["author", "ecole"])) |
                (Section.parent_section.has(Section.text.match(section_author_query) & Section._class.in_(["author", "ecole"])))
            ))
    if len(section_category_query) > 0:
        if not section_category_query.startswith('"') or not section_category_query.endswith('"'):
            section_category_query += '*'
        objects = objects.filter(
            Object.parent_section.has(
                (Section.text.match(section_category_query) & Section._class.in_(["category"])) |
                (Section.parent_section.has(Section.text.match(section_category_query) & Section._class.in_(["category"])))
            ))

    if len(actors_ids) > 0:
        objects = objects.filter(
            Object.sale.has(
                Sale.actors.any(
                    Actor.id.in_(actors_ids))))
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
    return objects
