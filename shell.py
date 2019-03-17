from app import create_app
from app.models import *
from app import db
app = create_app()
app.app_context().push()

