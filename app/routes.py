from app import app

@app.route('/')
def index():
    return "Hello World"


# from app import app

# @app.route('/')
# def index():
#     # return "Hello World"
#     return render_template('login.html')