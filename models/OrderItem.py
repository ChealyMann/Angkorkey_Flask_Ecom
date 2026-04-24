from extensions import db


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)  # អាច Null បើអត់មាន Variant

    qty = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    unit_discount = db.Column(db.Float, default=0.0)
    sub_total = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', lazy='joined')
    variants = db.relationship('ProductVariant')

    @property
    def display_name(self):
        if self.product and self.product.name:
            return self.product.name
        return f"Product #{self.product_id}"

    @property
    def variant_label(self):
        parts = []
        if self.variants:
            if self.variants.color:
                parts.append(self.variants.color)
            if self.variants.type:
                parts.append(self.variants.type)
        return " / ".join(parts) if parts else None

    @property
    def display_image(self):
        if self.variants and self.variants.images:
            primary_variant_image = next((img.image for img in self.variants.images if img.is_primary), None)
            if primary_variant_image:
                return primary_variant_image
            if self.variants.images[0].image:
                return self.variants.images[0].image

        if self.product and self.product.images:
            primary_product_image = next((img.image for img in self.product.images if img.is_primary), None)
            if primary_product_image:
                return primary_product_image
            if self.product.images[0].image:
                return self.product.images[0].image

        if self.product and self.product.image:
            return self.product.image

        return None
