from sqlalchemy import text

from models import Product, ProductImage
from extensions import db


def product_variant_images(product_id, variant_id):
    statement = text('SELECT * FROM product_image WHERE product_id = :product_id AND variant_id = :variant_id')
    query = db.session.execute(statement, {'product_id': product_id, 'variant_id': variant_id}).fetchall()

    product_images = []
    for item in query:
        product_images.append(
            ProductImage(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                image=item.image,
                is_primary=item.is_primary,
            )
        )

    return product_images