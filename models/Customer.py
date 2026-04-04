from extensions import db

class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20), nullable=True)

    locations = db.relationship(
        "CustomerLocation",
        backref="customer",
        lazy="select",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Customer {self.email}>"