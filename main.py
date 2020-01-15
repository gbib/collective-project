from app import create_app, db, cli
from app.models import User, BloodRequest
from app.utils.utils import populate_blood_group_table

app = create_app()
# with app.app_context():
#     populate_blood_group_table(db)
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'BloodRequest' :BloodRequest}