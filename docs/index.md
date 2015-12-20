![alt text](_static/prism_small.png "Flask-PRISM")

Flask-PRISM
=============

PRISM Is an simple way to manage your Flask APIs, providing consistent models, versions, access, and more while leaving you in full control. It's even super easy to use.


Check out this User model powered by Flask-SQLAlchemy and turned to JSON using PRISM:

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

Now in our API, let's say we want to return a list of all users. All we have to do is pass back any user objects from a PRISM **ReturnableResponse**

```python
from flask import Blueprint
from models import User
from flask.ext.prism import ReturnableResponse

bp = Blueprint('api', __name__, url_prefix="/api")

@bp.route('/users')
def api_users_get():
    return ReturnableResponse(User.query.all())

```

Which returns a nice clean and easy output
```json
[
    {
        "user_id": 1,
        "email": "some_email@internet.co",
        "first_name": "Roger"
    },
    {
        "user_id": 2,
        "email": "just@use.slack",
        "first_name": "Jennifer"
    }
]
```


### Topics

- [Getting started and installation](quickstart.html)
- [Versions](versions.html)
- [Permissions](permissions.html)
- [Advanced usage](advanced.html)






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



