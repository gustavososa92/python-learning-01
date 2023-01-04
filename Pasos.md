## Instalaciones Previas
Instalar python
Instalar plugin python en vscode
Instalar xampp

### 1 Configurar Proyecto
Crear carpeta para proyecto nuevo
Instalar virtual env y copiarlo en el proyecto
```py -m pip install virtualenv```
```py -m virtualenv python_modules```

Dentro de python_modules activar el perfil (ejecutar activate.bat)
fijarse que la terminal este activo el perfil

### 2 Instalar Flask
instalar dependencias
```pip install flask```

crear carpeta app y archivo python
importar Flask, jsonify
definir app
definir ruta
app run con debug en true

ejecutar archivo python

```python fileName.py```

### 3 Instalar dependencias para conexion de bd
```pip install flask-sqlalchemy```
```pip install flask-marshmallow```
```pip install marshmallow-sqlalchemy```
```pip install pymysql```

### 4 Configurar conexion a la base de datos
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #Base de datos 
ma = Marshmallow(app)#Esquemas

app.app_context().push()
```

### 5 Crear una tabla en la base de datos ej
```python
class Categoria(db.Model):
    cat_id = db.Column(db.Integer, primary_key=True)
    cat_nom = db.Column(db.String(100))
    cat_desp = db.Column(db.String(100))

    def __init__(self,cat_nom,cat_desp):
        self.cat_nom = cat_nom
        self.cat_desp = cat_desp

db.create_all()
```
### 6 Crear esquemas para recibir la info de la bd

```python
class CategoriaSchema(ma.Schema):
    class Meta:
        fields = ('cat_id','cat_nom','cat_desp')

#Una respuesta
categoria_schema = CategoriaSchema()
#mas de una respuesta
categorias_schema = CategoriaSchema(many=True)
```

### 7 Crear endpoint get all

popular base de datos con informacion

```python
@app.route('/categoria',methods=['GET'])
def get_categoria():
    all_categoria =Categoria.query.all()
    result = categorias_schema.dump(all_categoria)
    return jsonify(result)
```

### 8 Crear endpoint get by id
```python
@app.route('/categoria/<id>', methods=['GET'])
def get_categoria_by_id(id):
    una_categoria = Categoria.query.get(id)
    return categoria_schema.jsonify(una_categoria)
```

### 9 Crear endpoint post
importar de flask ```request```

```python
@app.route('/categoria', methods=['POST'])  # Crear una nueva categoria
def insert_categoria():
    data = request.get_json(force=True)
    cat_nom = data['cat_nom']
    cat_desp = data['cat_desp']

    nuevo_registro = Categoria(cat_nom, cat_desp)

    db.session.add(nuevo_registro)
    db.session.commit()
    return categoria_schema.jsonify(nuevo_registro)
```

### 10 Crear endpoint update

```python
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
```

### 11 Crear endpoint delete

```python
@app.route('/categoria/<id>', methods=['DELETE'])  # Delete de categoria by id, cambiar por baja logica...
def delete_categoria_by_id(id):
    una_categoria = Categoria.query.get(id)

    db.session.delete(una_categoria)
    db.session.commit()

    return categoria_schema.jsonify(una_categoria)
    ```