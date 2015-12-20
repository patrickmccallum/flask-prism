
    
![alt text](http://patsnacks.com/wp-content/uploads/2015/10/524x128xflask-font-prism-02-e1444044468717.png.pagespeed.ic.e09xraLMJj.png "Flask-PRISM")

PRISM Is an simple way to manage your Flask APIs, providing consistent models, versions, access, and more while leaving you in full control. It's even super easy to use.

Check out this Flask-SQLAlchemy model using PRISM:

```
from prism import p

class User(db.Model, UserMixin):

    # Define table name
    __tablename__ = 'users'
 
    # Primary key, user ID
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
 
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
    
Now in our API, let's say we want to return a list of all users. All we have to do is pass back any user objects from a PRISM **ReturnableResponse**

```
from flask import Blueprint
from models import User
from flask.ext.prism import ReturnableResponse

bp = Blueprint('api', __name__, url_prefix="/api")

@bp.route('/users')
def api_users_get():
    return ReturnableResponse(User.query.all())

```
    
    
Features
--------

- Easily manage your JSON models from a predictable location
- Insert permission based rules into your JSON output
- Models and permission checks can be easily versioned by passing a ``version=INTEGER`` parameter




### Installation

You can grab Flask-PRISM using pip (our Pypi page is over here <https://pypi.python.org/pypi?name=Flask-PRISM&:action=display> )

```sh
$ pip install Flask-PRISM
```

Instantiate our **Prism** object in a separate file, in this example it's in ``prism.py``
```python
from flask.ext.prism import Prism

p = Prism()
```

And finally, call ``init_app()`` during setup.
```python
from flask import Flask
from flask.ext.prism import ReturnableResponse
from prism import p

from models import User

# Setup flask like we normally do
app = Flask(__name__)

# Setup PRISM to see Flask
p.init_app(prism)

@app.route('/api/user/<user_id>')
def api_user_get(user_id):
    return ReturnableResponse(User.query.get(user_id))
    
if __name__ == '__main__':
    app.run()
```




### Development

Want to contribute? Awesome!  
If you've made a change you think will help other PRISM users, just open a merge request or an issue on GitHub.

If you're not already there, it's over at <https://github.com/patrickmccallum/flask-prism>


### Changelog
##### 0.2.2
    
- Added documentation
    
##### 0.2.1
 - Initial release


### License


Flask-PRISM is distributed under the MIT license. See the LICENSE file included in this project for more.





