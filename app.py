
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, jsonify, request, make_response


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = True


# flask swagger configs
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Drinks API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# create db instance
db = SQLAlchemy(app)

# instanctiate ma
ma = Marshmallow(app)


class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __repr__(self):
        return f"{self.name} - {self.description}"


class DrinksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')


# instantiate schema objects for todolist and todolists
drinklist_schema = DrinksSchema(many=False)
drinklists_schema = DrinksSchema(many=True)


@app.route('/')
def index():
    return 'Hello!'


@app.route('/drinks')
def getAllDrinks():
    drinks = Drink.query.all()
    output = []
    for item in drinks:
        drink_data = {"name": item.name,
                      'description': item.description
                      }
        output.append(drink_data)

    return {"drinks": output}


@app.route('/drinks/<id>')
def getDrinkById(id):
    drink = Drink.query.get_or_404(id)
    return {"name": drink.name, 'description': drink.description, 'id': drink.id}


@app.route('/drinks', methods=['POST'])
def add_drink():
    drink = Drink(name=request.json['name'], description=request.json['description'])
    db.session.add(drink)
    db.session.commit()
    return {"id": drink.id}


@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"error": "No such drink"}
    db.session.delete(drink)
    db.session.commit()
    return {"message": "drink deleted"}


@app.errorhandler(400)
def handle_400_error(_error):
    """Return a http 400 error to client"""
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@app.errorhandler(401)
def handle_401_error(_error):
    """Return a http 401 error to client"""
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@app.errorhandler(404)
def handle_404_error(_error):
    """Return a http 404 error to client"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    """Return a http 500 error to client"""
    return make_response(jsonify({'error': 'Server error'}), 500)


if __name__ == '__main__':
    app.run(debug=True)
