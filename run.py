import os

from app import create_app, db

app = create_app()

with app.app_context():
    if not os.path.exists('databas.db'):
        db.create_all()
        print("Database created!")

if __name__ == '__main__':
    app.run(debug=True)
