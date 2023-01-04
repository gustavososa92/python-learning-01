from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

app.app_context().push()


class Categoria(db.Model):
    cat_id = db.Column(db.Integer, primary_key=True)
    cat_nom = db.Column(db.String(100))
    cat_desp = db.Column(db.String(100))

    def __init__(self, cat_nom, cat_desp):
        self.cat_nom = cat_nom
        self.cat_desp = cat_desp


db.create_all()


class CategoriaSchema(ma.Schema):
    class Meta:
        fields = ('cat_id', 'cat_nom', 'cat_desp')


# Una respuesta
categoria_schema = CategoriaSchema()
# mas de una respuesta
categorias_schema = CategoriaSchema(many=True)


@app.route('/categoria', methods=['GET'])  # Get de categoria
def get_categoria():
    all_categoria = Categoria.query.all()
    result = categorias_schema.dump(all_categoria)
    return jsonify(result)


@app.route('/categoria/<id>', methods=['GET'])  # Get de categoria by id
def get_categoria_by_id(id):
    una_categoria = Categoria.query.get(id)
    return categoria_schema.jsonify(una_categoria)


@app.route('/categoria', methods=['POST'])  # Crear una nueva categoria
def insert_categoria():
    data = request.get_json(force=True)
    cat_nom = data['cat_nom']
    cat_desp = data['cat_desp']

    nuevo_registro = Categoria(cat_nom, cat_desp)

    db.session.add(nuevo_registro)
    db.session.commit()
    return categoria_schema.jsonify(nuevo_registro)


@app.route('/categoria/<id>', methods=['PUT'])  # Update de categoria by id
def update_categoria_by_id(id):
    una_categoria = Categoria.query.get(id)

    data = request.get_json(force=True)
    cat_nom = data['cat_nom']
    cat_desp = data['cat_desp']

    una_categoria.cat_nom = cat_nom
    una_categoria.cat_desp = cat_desp

    db.session.commit()

    return categoria_schema.jsonify(una_categoria)

@app.route('/categoria/<id>', methods=['DELETE'])  # Delete de categoria by id, cambiar por baja logica...
def delete_categoria_by_id(id):
    una_categoria = Categoria.query.get(id)

    db.session.delete(una_categoria)
    db.session.commit()

    return categoria_schema.jsonify(una_categoria)


@app.route('/', methods=['GET'])  # Mensaje de bienvenida
def index():
    return jsonify({'Mensaje': 'Bienvenido'})


if __name__ == '__main__':
    app.run(debug=True)
