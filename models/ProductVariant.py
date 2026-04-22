from extensions import db

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    sku = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    purchase_cost = db.Column(db.Numeric(10, 2), nullable=True)
    physical_stock = db.Column(db.Integer, nullable=True)
    reserved_stock = db.Column(db.Integer, nullable=True)
    discount_price = db.Column(db.Numeric(10, 2), nullable=True)
    images = db.relationship('ProductImage', backref='variant', lazy=True)

    @property
    def available_stock(self):
        return max((self.physical_stock or 0) - (self.reserved_stock or 0), 0)

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price is not None else self.price

    @property
    def profit_per_item(self):
        if self.purchase_cost is None:
            return None
        return self.effective_price - self.purchase_cost


    def __repr__(self):
        return f'<ProductVariant {self.sku} for Product {self.product_id}>'


