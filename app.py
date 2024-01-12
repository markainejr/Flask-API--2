from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# Product Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
       model = Product
       fields = ("id", "name", "description", "price", "qty")
# Initialize schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


    # Create a Product
@app.route('/product', methods=['POST'])
def add_product():
    try:
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']

        new_product = Product(name=name, description=description, price=price, qty=qty)
        db.session.add(new_product)
        db.session.commit()

        return product_schema.jsonify(new_product), 201  # Return status code 201 for created
    except KeyError:
        return jsonify({"message": "Missing required fields"}), 400  # Return status code 400 for bad request


# Get All Products
@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)

# Get A single product
@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if product:
        return product_schema.jsonify(product)
    return jsonify({"message": "Product not found"}), 404

# Update a Product
@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        # Retrieve the product from the database
        product = Product.query.get(id)
        if not product:
            return jsonify({"message": "Product not found"}), 404
        
        # Extract data from the request JSON
        data = request.json    
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        qty = data.get('qty')

        # Check for missing required fields
        if not name or not description or price is None or  qty is None:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Update product information
        product.name = name
        product.description = description
        product.price = price
        product.qty = qty

        # Commit changes to the database
        db.session.commit()

        # Return updated product information
        return product_schema.jsonify(product), 200
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500
    
# Delete a product
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    if product:
        return product_schema.jsonify(product)
    return jsonify({"message": "Product not found"}), 404

# Run Server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)       