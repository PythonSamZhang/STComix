from flask_avatars import Avatars
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES

bootstrap = Bootstrap()
bebel = Babel()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
books = UploadSet('books', IMAGES)
dropzone = Dropzone()
moment = Moment()
avatars = Avatars()
