Flask-PRISM
=============

### Getting started and installation

##### Download

You can grab Flask-PRISM using pip (our Pypi page is over [here](https://pypi.python.org/pypi?name=Flask-PRISM&:action=display))

```sh
$ pip install Flask-PRISM
```

Or from the [GitHub page](https://github.com/patrickmccallum/flask-prism) (if you like doing stuff manually)

##### Setting up our project

Like a lot of Flask extensions out there (SQLAlchemy for example), PRISM needs a file of its own to call home. Or at least somewhere where it can be imported almost everywhere in your project that won't cause issues. 

In this example, I'm going to create a file called ``prism.py``, and in it instantiate our new **Prism** object.
```python
from flask.ext.prism import Prism

p = Prism()
```

And now when I setup my app I'll just import that ``p`` object and call ``p.init_app(app)``.

```python
from flask import Flask
from flask.ext.prism import Refract
from prism import p

from models import User

# Setup flask like we normally do
app = Flask(__name__)

# Setup PRISM to see Flask
p.init_app(app)
    
if __name__ == '__main__':
    app.run()
```

And that's all there is to it! 

To recap, our new project structure looks a little something like

```text
myProjectDir/
    static/
    templates/
    server.py # Where we setup our flask server (call this file anything you like)
    prism.py # Keeping the Prism object in here
```

##### Make our Model responsive

Any object in your project can be made *Responsive* so you can push it out through the API with PRISM, more advanced usages are covered later on in this documentation but in this example we'll go over making our SQLAlchemy **User** model *Responsive* and then setup up an API to interact with it.

Let's start by making a **user.py** file under ``myProjectDir/models/user.py`` (don't forget to also put an __init__.py in there)


```python
from prism import p
from database import db

class User(db.Model):

    # Define table name
    __tablename__ = 'users'
 
    # Primary key, user ID
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
 
    # First name
    first_name = db.Column(db.String(255))

    # Email
    email = db.Column(db.String(255))
 
    # Password
    password = db.Column(db.String(255))
 
    @p.api_representation()
    def as_data(self):
        return {
            'id': self.user_id,
            'email': self.email,
            'first_name': self.first_name
        }
```

It's business as usual, but with PRISM we can add the ``@p.api_representation()`` wrapper to a method which shows how our **User** model will appear when passed out of the API.

The ``api_representation`` wrapper supports a few optional parameters:
 - api_representation(**version** *[=None]*) - **Integer**
    The version is used to manage which version of the API this representation is used for. This is covered fully under the [versions guide](versions.html).
 - api_representation(**mimetype** *[=None]*) - **String**
    Convenience method to change the final mimetype of the response. This can be done in other places and shouldn't really be used here.
    
Now let's start building our first API using PRISM. Just to keep the theme going let's put our API routes under ``myProjectDir/api/api_routes_user.py``

```python
from flask import Blueprint
from flask.ext.prism import Refract

from models.user import User
from prism import p

bp = Blueprint('api_user_v1', __name__, url_prefix="/api/v1/users")

@bp.route('/')
def api_v1_users_get():
    return Refract(User.query.all())
    
@bp.route('/<int:user_id>')
def api_v1_user_get(user_id):
    return Refract(User.query.get(user_id))
    
```

How easy is that? 

You can pass a single or many objects into the **Refract** object (which behaves exactly like a normal Flask **Response**) but with a few extra optional parameters:
- Refract(**version** *[=None]*) - **Integer**

    When you specify a version here and in your *api_representation* method, you can tell the response exactly which version of your model to show here.
- Refract(**as_list** *[=False]*) - **String**

    When you pass multiple objects into a **Returnable Response** the JSON is automatically formatted as an *array*, but when only a single object is passed it behaves like an *object*. When **as_list** is true, it forces the output to always be formatted as a JSON *array*.
- Refract(**mimetype** *[=None]*) - **String**

    Just like the base Flask **Response** you can specify a mimetype here.
- Refract(**status** *[=200]*) - **String**

    Just like the base Flask **Response** you can specify a status code here.
 
 
All that's left is to register the blueprint under ``server.py``


```python
from flask import Flask
from flask.ext.prism import Refract
from prism import p

from models import User
from api.api_routes_user import bp as api_bp_users

# Setup flask like we normally do
app = Flask(__name__)

# Setup PRISM to see Flask
p.init_app(app)

# Register our users blueprint
app.register_blueprint(api_bp_users)
    
if __name__ == '__main__':
    app.run()
```



Want to learn more about what PRISM can do? Check out these other topics:

- [Overview](index.html)
- [Versions](versions.html)
- [Permissions](permissions.html)
- [Advanced usage](advanced.html)
