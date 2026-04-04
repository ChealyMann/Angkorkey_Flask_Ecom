from extensions import db
class CustomerLocation(db.Model):
    __tablename__ = "customer_location"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    label = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<CustomerLocation {self.address}>"