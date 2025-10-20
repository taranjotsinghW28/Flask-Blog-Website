from app import create_app, db
from app.models import User, Post, Comment

app = create_app()

# This part is optional but useful for creating the database and tables
# if you don't use Flask-Migrate
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
