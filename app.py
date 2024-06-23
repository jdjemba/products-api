from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api, Resource, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db/db_eemi_class'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app, version='1.0', title='Store API',
          description='A simple API for managing products, users, and orders')

ns = api.namespace('api', description='Store operations')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'discount_price': self.discount_price,
            'rating': self.rating
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'user': self.user.to_dict(),
            'product': self.product.to_dict()
        }


product_model = api.model('Product', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a product'),
    'name': fields.String(required=True, description='Product name'),
    'category': fields.String(required=True, description='Product category'),
    'price': fields.Float(required=True, description='Product price'),
    'discount_price': fields.Float(description='Discounted price'),
    'rating': fields.Float(description='Product rating')
})

user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email')
})

order_model = api.model('Order', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of an order'),
    'user_id': fields.Integer(required=True, description='User ID'),
    'product_id': fields.Integer(required=True, description='Product ID'),
    'quantity': fields.Integer(required=True, description='Quantity ordered'),
    'total_price': fields.Float(required=True, description='Total price')
})


@ns.route('/products')
class ProductList(Resource):
    @ns.doc('list_products')
    @ns.marshal_list_with(product_model)
    def get(self):
        """List all products"""
        products = Product.query.all()
        return [product.to_dict() for product in products]

    @ns.doc('create_product')
    @ns.expect(product_model)
    @ns.marshal_with(product_model, code=201)
    def post(self):
        """Create a new product"""
        data = request.get_json()
        new_product = Product(
            name=data['name'],
            category=data['category'],
            price=data['price'],
            discount_price=data.get('discount_price'),
            rating=data.get('rating')
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product.to_dict(), 201

@ns.route('/products/<int:id>')
class ProductResource(Resource):
    @ns.doc('get_product')
    @ns.marshal_with(product_model)
    def get(self, id):
        """Fetch a product given its identifier"""
        product = Product.query.get_or_404(id)
        return product.to_dict()

    @ns.doc('update_product')
    @ns.expect(product_model)
    @ns.marshal_with(product_model)
    def put(self, id):
        """Update a product given its identifier"""
        data = request.get_json()
        product = Product.query.get_or_404(id)
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.price = data.get('price', product.price)
        product.discount_price = data.get('discount_price', product.discount_price)
        product.rating = data.get('rating', product.rating)
        db.session.commit()
        return product.to_dict()

    @ns.doc('delete_product')
    def delete(self, id):
        """Delete a product given its identifier"""
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return '', 204

@ns.route('/users')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        users = User.query.all()
        return [user.to_dict() for user in users]

    @ns.doc('create_user')
    @ns.expect(user_model)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = request.get_json()
        new_user = User(
            name=data['name'],
            email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict(), 201

@ns.route('/orders')
class OrderList(Resource):
    @ns.doc('list_orders')
    @ns.marshal_list_with(order_model)
    def get(self):
        """List all orders"""
        orders = Order.query.all()
        return [order.to_dict() for order in orders]

    @ns.doc('create_order')
    @ns.expect(order_model)
    @ns.marshal_with(order_model, code=201)
    def post(self):
        """Create a new order"""
        data = request.get_json()
        user = User.query.get_or_404(data['user_id'])
        product = Product.query.get_or_404(data['product_id'])
        quantity = data['quantity']
        total_price = quantity * product.price  # or use discount_price if applicable
        new_order = Order(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order.to_dict(), 201


if __name__ == '__main__':
    app.run(debug=True, port=8001, host='0.0.0.0')

