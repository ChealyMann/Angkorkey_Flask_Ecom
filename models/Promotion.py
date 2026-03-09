from extensions import db

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    subtitle = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    button_text = db.Column(db.String(50), default="Shop Now")
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Promotion {self.title}>'
