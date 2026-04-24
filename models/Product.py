import math

from flask import request
from flask_paginate import get_page_parameter, Pagination
from sqlalchemy import text

from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    cost = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(5), nullable=False)
    has_variants = db.Column(db.Boolean, default=False, nullable=False)

    images = db.relationship('ProductImage', backref='product', lazy=True)
    category_name = db.relationship('Category', backref='product', lazy=True)
    variants = db.relationship('ProductVariant', backref='product', lazy=True)

    def __repr__(self):
        return f'Product {self.name}'


def getAllProduct():
    page = request.args.get(get_page_parameter(), default=1, type=int)
    per_page = 6
    offset_value = (page - 1) * per_page

    sql = text("""
               SELECT p.*, c.name as "category_name"
               FROM product p
                        INNER JOIN category c ON c.id = p.category_id LIMIT :limit
               OFFSET :offset
               """)

    results = db.session.execute(sql, {'limit': per_page, 'offset': offset_value}).fetchall()

    rows = text(
        """
        select COUNT(*)
        from product;
        """
    )
    _rows = db.session.execute(rows).fetchone()[0]

    pagination = Pagination(page=page, per_page=per_page, total=_rows, css_framework='bootstrap5')

    _results = {
        'list': results,
        'pagination': pagination,
    }

    return _results


import json
from sqlalchemy import text

def getProductDetail(product_id: int):
    sql = text("""
        SELECT 
            p.id AS product_id,
            p.name,
            p.desc,
            (
                SELECT JSON_GROUP_ARRAY(
                    JSON_OBJECT(
                        'id', pi.id,
                        'image', pi.image,
                        'is_primary', pi.is_primary
                    )
                )
                FROM product_image pi
                WHERE pi.product_id = p.id AND pi.variant_id IS NULL
            ) AS general_images,
            (
                SELECT JSON_GROUP_ARRAY(
                    JSON_OBJECT(
                        'color', pv.color,
                        'types', (
                            SELECT JSON_GROUP_ARRAY(
                                JSON_OBJECT(
                                    'variant_id', pv2.id,
                                    'sku', pv2.sku,
                                    'attribute_label', TRIM(SUBSTR(pv2.type, 1, INSTR(pv2.type, ':') - 1)),
                                    'attribute_value', TRIM(SUBSTR(pv2.type, INSTR(pv2.type, ':') + 1)),
                                    'original_price', pv2.price,
                                    'discount_price', pv2.discount_price,
                                    'available_stock', (pv2.physical_stock - pv2.reserved_stock),
                                    'stock_status', CASE
                                        WHEN (pv2.physical_stock - pv2.reserved_stock) <= 0 THEN 'out_of_stock'
                                        WHEN (pv2.physical_stock - pv2.reserved_stock) <= 10 THEN 'low_stock'
                                        ELSE 'in_stock'
                                    END,
                                    'images', (
                                        SELECT JSON_GROUP_ARRAY(
                                            JSON_OBJECT('id', pi2.id, 'image', pi2.image, 'is_primary', pi2.is_primary)
                                        )
                                        FROM product_image pi2
                                        WHERE pi2.variant_id = pv2.id
                                    )
                                )
                            )
                            FROM product_variants pv2
                            WHERE pv2.product_id = p.id AND pv2.color = pv.color
                        )
                    )
                )
                FROM (SELECT DISTINCT color FROM product_variants WHERE product_id = p.id) pv
            ) AS color_groups
        FROM product p
        WHERE p.id = :product_id
    """)

    row = db.session.execute(sql, {"product_id": product_id}).fetchone()

    if not row:
        return None

    color_groups = json.loads(row.color_groups) if row.color_groups else []

    for group in color_groups:
        group["types"] = json.loads(group["types"]) if isinstance(group["types"], str) else group["types"]
        for variant in group["types"]:
            variant["images"] = json.loads(variant["images"]) if isinstance(variant["images"], str) else (variant["images"] or [])
            # Remove discount_price key entirely if null
            if variant.get("discount_price") is None:
                variant.pop("discount_price", None)

    return {
        "product_id": row.product_id,
        "name": row.name,
        "description": row.desc,
        "general_images": json.loads(row.general_images) if row.general_images else [],
        "color_groups": color_groups
    }