from extensions import db

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'),nullable =True)
    image = db.Column(db.String(120))
    is_primary = db.Column(db.Integer, default = 0)