from flask import abort, redirect

from extensions import db
from sqlalchemy.sql import text
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),unique = True,nullable = False)
    desc = db.Column(db.String(255))
    image = db.Column(db.String(255))
    status = db.Column(db.String(5), nullable = False)

    def __repr__(self):
        return '<Category %r>' % self.name



def getCategoryById(category_id):
    sql = text("select * from category where id = :category_id")
    result = db.session.execute(sql, {'category_id': category_id})
    if result:
        return result.fetchone()
    return redirect('backend/admin/category/add')
