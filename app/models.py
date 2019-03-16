# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Table
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.formatters import StrippedString
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class Actor(SearchableMixin, db.Model):
    __tablename__ = 'actor'
    __searchable__ = ['first_name', 'last_name', 'role']

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(65))
    last_name = db.Column(db.String(45), nullable=False)
    role = db.Column(db.String(45))

    sales = db.relationship('Sale', secondary='actor_sale', backref='actors')

    def __repr__(self):
        return "<Actor (first_name='%s', last_name='%s', role='%s')"%(self.first_name, self.last_name, self.role)


t_actor_sale = db.Table(
    'actor_sale',
    db.Column('actor_id', db.ForeignKey('actor.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    db.Column('sale_id', db.ForeignKey('sale.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True)
)


class Object(SearchableMixin, db.Model):
    __tablename__ = 'object'
    __table_args__ = (
        db.Index('parent section object_idx', 'parent_section_sale', 'parent_section_page', 'parent_section_entity'),
    )
    __searchable__ = ['text']

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.ForeignKey('sale.id'), nullable=False, index=True)
    page = db.Column(db.Float(asdecimal=True), nullable=False)
    entity = db.Column(db.Integer, nullable=False)
    parent_section_id = db.Column(db.ForeignKey('section.id'), index=True)
    parent_section_sale = db.Column(db.Integer)
    parent_section_page = db.Column(db.Float(asdecimal=True))
    parent_section_entity = db.Column(db.Integer)
    num_ref = db.Column(db.String(45))
    text = db.Column(db.String, nullable=False, index=True)
    bbox = db.Column(db.String(45), nullable=False)
    inha_url = db.Column(db.String(175), nullable=False)
    iiif_url = db.Column(db.String(175))

    def get_parent_sections(self):
        sections = []
        if self.parent_section_sale is None:
            return None
        parent = Section.query.filter(Section.id==self.parent_section_id).first()
        sections.append(parent)
        parent_parent = parent.get_parent_section()
        if parent_parent is not None:
            sections.append(parent_parent)
        return sections

    def __repr__(self):
        return "<Object (sale_id=%d, page=%f, entity=%d, text='%s')"%(self.sale_id, self.page, self.entity, self.text)

    parent_section = db.relationship('Section', primaryjoin='Object.parent_section_id == Section.id', backref='objects')
    sale = db.relationship('Sale', primaryjoin='Object.sale_id == Sale.id', backref='objects')


class Sale(db.Model):
    __tablename__ = 'sale'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    cote_inha = db.Column(db.String(45), nullable=False)
    url_inha = db.Column(db.String(75), nullable=False)


class Section(SearchableMixin, db.Model):
    __tablename__ = 'section'
    __table_args__ = (
        db.Index('parent section_idx', 'parent_section_page', 'parent_section_sale', 'parent_section_entity'),
        db.Index('parent_section', 'parent_section_sale', 'parent_section_page', 'parent_section_entity')
    )
    __searchable__ = ['text']

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.ForeignKey('sale.id'), nullable=False, index=True)
    page = db.Column(db.Float(asdecimal=True), nullable=False)
    entity = db.Column(db.Integer, nullable=False)
    parent_section_id = db.Column(db.ForeignKey('section.id'), index=True)
    parent_section_sale = db.Column(db.Integer)
    parent_section_page = db.Column(db.Float(asdecimal=True))
    parent_section_entity = db.Column(db.Integer)
    _class = db.Column('class', db.String(25, 'utf8mb4_unicode_ci'), nullable=False)
    text = db.Column(db.String(collation='utf8mb4_unicode_ci'), nullable=False, index=True)
    bbox = db.Column(db.String(45, 'utf8mb4_unicode_ci'), nullable=False)
    inha_url = db.Column(db.String(175, 'utf8mb4_unicode_ci'), nullable=False)
    iiif_url = db.Column(db.String(175, 'utf8mb4_unicode_ci'))

    def get_parent_section(self):
        if self.parent_section_sale is None:
            return None
        return Section.query.filter(Section.sale_id==self.parent_section_sale,
                                    Section.page==self.parent_section_page,
                                    Section.entity==self.parent_section_entity).first()

    def __repr__(self):
        return "<Section (sale_id=%d, page=%f, entity=%d, text='%s')"%(self.sale_id, self.page, self.entity, self.text)

    parent_section = db.relationship('Section', remote_side=[id], primaryjoin='Section.parent_section_id == Section.id', backref='sections')
    sale = db.relationship('Sale', primaryjoin='Section.sale_id == Sale.id', backref='sections')
