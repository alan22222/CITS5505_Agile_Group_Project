# CITS5505_Agile_Group_Project - OneClickML

## Contribution
Members of Group 39:
| **UWA ID** | **Name**       | **GitHub Username(s)**       |
|------------|----------------|------------------------------|
| 24085576   | Alan Chacko    | alan22222                   |
| 24239318   | Ayden Pan      | Pixy-greenhand              |
| 24302286   | Yee Man Tsai   | ym-Tsai                     |
| 24256987   | Yanchen Yu     | wizardG7777777, Yanchen Yu  |


## Purpose, Design and use of OneClickML
This application is a powerful data analysis tool designed to simplify the process of identifying the most suitable machine learning model for any dataset with just one click. 

Users can register and log in to access a user-friendly dashboard. From there, they can upload datasets in CSV format, which are validated before proceeding. Once validated, users can select a machine learning model and processing speed. The backend processes the data and provides detailed insights and analysis.

Currently, the app supports three core machine learning models: Linear Regression, SVM, and K-Means, along with three processing speed options.
 
 
 ## Instruction of launching the OneClickML app
OneClickML is using Flask structure, backed by SQL-Alchemy and are based in Python.

1. Ensure python3 is supported in the running machine. The stable version of Python we support is 3.10.
2. Install virtual environment using the cmd line: `python -m venv venv`
3. Activate the virtual environment using the cmd line: `source venv/bin/activate`
4. Install the required packages using the cmd line: `pip install -r requirements.txt`
5. Run the following cmd line and open the app with the shown link: `python run.py` (the link should be shown in something that is similar to "* Running on http://127.0.0.1:5000")

Remark: If you encounter the scipy error (it is an error about the "metadata", e.g. `Preparing metadata (pyproject.toml) did not run successfully.`) when you try to install the requirements.txt, please use `python3 --version` to check your Python version. If your version exceeds `3.10`, you should downgrade your Python version to `3.10`.

Below are some other common commands you may need when you run the app:
0. First time installing Flask: `pip install Flask`
1. Clone the Repository: `git clone "link"` and then `cd (project folder)`
2. Run Database Migration: `flask db migrate` and `flask db upgrade`
3. Start the Flask Application: `flask run`


## Instuction of running the tests for the app
TBC
