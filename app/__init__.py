from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(debug=True)

import app.routes

# from flask import Flask

# app = Flask(__name__)

# import app.routes  # Ensure routes are imported after app is created
