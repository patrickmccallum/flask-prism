![alt text](_static/prism_small.png "Flask-PRISM")

Flask-PRISM
=============

PRISM is a simple way to manage your Flask APIs, providing consistent models, version management, access control, and more while leaving you in full control of your code. It's even super easy to use.

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

Now in our API let's set up a route to return all users. All we do is return our Flask-SQLAlchemy models through a PRISM **Refract**

```python
from flask import Blueprint
from models import User
from flask.ext.prism import Refract

bp = Blueprint('api', __name__, url_prefix="/api")

@bp.route('/users')
def api_users_get():
    return Refract(User.query.all())

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
If you've made a change you think will help other PRISM users, just open a pull request or raise an issue on GitHub.

If you're not already there, it's over at <https://github.com/patrickmccallum/flask-prism>


### Changelog
##### 0.4.0 BREAKING CHANGES
- Renamed Refract to Refract, shorter, makes more sense given the context
- Fixed new line issue in response mapping

##### 0.3.2
- Fixed an issue with the as_list parameter that could cause it to be ignored in certain cases

##### 0.3.1
- Fixed issue that would cause deployments to fail with Apache's mod_wsgi, and subsequently AWS Elastic Beanstalk

##### 0.3.0
- PRISM representations can now contain other objects with representations! They'll be auto converted on the way out
- Removed stray print statements used for debugging

##### 0.2.2
- Added documentation

##### 0.2.1
 - Initial release


Flask-PRISM is distributed under the MIT license. See the LICENSE file included in this project for more.



