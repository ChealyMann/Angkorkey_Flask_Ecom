from extensions import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(64), nullable=False)
    image = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return "<User %r>" % self.username
