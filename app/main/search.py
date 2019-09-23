import dateutil.parser as date_parse
from app.models import Actor, Object, Sale, Section


def search(actors_ids,
           object_query,
           section_author_query,
           section_category_query,
           start_date,
           end_date):
    objects = Object.query
    if len(object_query) > 0:
        object_query = wildcard_query(object_query)
        objects = objects.filter(Object.text.match(object_query))
    if len(section_author_query) > 0:
        section_author_query = wildcard_query(section_author_query)
        objects = filter_section_by_classes(objects, section_author_query, ['author', 'ecole'])
    if len(section_category_query) > 0:
        section_category_query = wildcard_query(section_category_query)
        objects = filter_section_by_classes(objects, section_category_query, ['category'])

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


def wildcard_query(query):
    if not query.startswith('"') or not query.endswith('"'):
        query += '*'
    return query


def filter_section_by_classes(objects, query, classes):
    return objects.filter(
        Object.parent_section.has(
            (Section.text.match(query) &
             Section._class.in_(classes)) |
            (Section.parent_section.has(
                Section.text.match(query) &
                Section._class.in_(classes)))
        ))
