from extensions import db

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    sku = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    physical_stock = db.Column(db.Integer, nullable=True)
    reserved_stock = db.Column(db.Integer, nullable=True)
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)
    images = db.relationship('ProductImage', backref='variant', lazy=True)

    def __repr__(self):
        return f'<ProductVariant {self.sku} for Product {self.product_id}>'

