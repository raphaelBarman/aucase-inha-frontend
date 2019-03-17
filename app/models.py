# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Table
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from app import db
import math
from app.formatters import StrippedString
from app.search import add_to_index, remove_from_index, query_index
from sqlalchemy_fulltext import FullText


def object2iiif(obj, scale=0.1):
    if obj.iiif_url is None:
        return ""
    iiif_url = obj.iiif_url
    xmin, ymin, xmax, ymax = eval(obj.bbox)
    w = xmax-xmin
    h = ymax-ymin
    xmin = math.floor(xmin-w*scale)
    ymin = math.floor(ymin-h*scale)
    w = math.ceil(w+w*scale*2)
    h = math.ceil(h+h*scale*2)
    return "%s/%d,%d,%d,%d/full/0/default.jpg" % (iiif_url, xmin, ymin, w, h)

class Actor(db.Model):
    __tablename__ = 'actor'
    __searchable__ = ['first_name', 'last_name', 'role']

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(65))
    last_name = db.Column(db.String(45), nullable=False)
    role = db.Column(db.String(45))

    sales = db.relationship('Sale', secondary='actor_sale', backref='actor_sales')

    def __repr__(self):
        return "<Actor (first_name='%s', last_name='%s', role='%s')"%(self.first_name, self.last_name, self.role)

    def full_name(self):
        return "%s%s" % (
                self.first_name + " " if len(self.first_name) > 0 else "",
                self.last_name)


t_actor_sale = db.Table(
    'actor_sale',
    db.Column('actor_id', db.ForeignKey('actor.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    db.Column('sale_id', db.ForeignKey('sale.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True)
)


class Object(FullText, db.Model):
    __tablename__ = 'object'
    __table_args__ = (
        db.Index('parent section object_idx', 'parent_section_sale', 'parent_section_page', 'parent_section_entity'),
    )
    __fulltext_columns__ = ('text')

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

    actors = db.relationship('Actor', secondary='actor_sale', backref='sale_actors')


class Section(db.Model):
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
