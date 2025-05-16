# 🚀 CITS5505_Agile_Group_Project - OneClickML

## 👥 Contribution

Members of Group 39:

| **UWA ID** | **Name**       | **GitHub Username(s)**       |
|------------|----------------|------------------------------|
| 24085576   | Alan Chacko    | alan22222                    |
| 24239318   | Ayden Pan      | Pixy-greenhand               |
| 24302286   | Yee Man Tsai   | ym-Tsai                      |
| 24256987   | Yanchen Yu     | wizardG7777777, Yanchen Yu   |

---

## 🎯 Purpose, Design, and Use of OneClickML

OneClickML is a smart, streamlined data analysis platform that empowers users to discover the best machine learning model for their dataset — with just one click.

### 🔍 Key Features:
- Simple registration and login system
- CSV upload and validation
- One-click ML model execution
- Customizable processing speed
- Dashboard with visual insights

### 🧠 Supported Machine Learning Models:
- Linear Regression
- Support Vector Machine (SVM)
- K-Means Clustering

---

## ⚙️ Instructions for Launching the OneClickML App

OneClickML is developed using **Flask** and **SQLAlchemy**, and is written in **Python 3.10**.

### Folder Setup Steps:
1. Unzip the folder
2. Locate the unzipped file
3. For Windows, use Powershell; For MacOS, use Terminal


### 🛠️ Initial Setup

1. Clone this repository:
```bash
git clone https://github.com/alan22222/CITS5505_Agile_Group_Project.git
cd <project-folder>
```

2. Ensure Python 3.10 is installed:
```bash
python3 --version
```

### 🔧 Setup Steps:

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup the local SQLite database (for the first time):
```bash
flask db upgrade
```

5. Run the app:
```bash
python run.py
```

OR 

5. Run the app:
```bash
flask run

```

After launching, you should see:
```
* Running on http://127.0.0.1:5000
```

6. Use browser to open
```
http://127.0.0.1:5000
```

---

### ⚠️ Python Version Compatibility

If you encounter this error when installing dependencies:
```
Preparing metadata (pyproject.toml) did not run successfully.
```
Your Python version might be too new. Run:
```bash
python3 --version
```
If it's above `3.10`, consider downgrading to Python 3.10.

---

### 🛠️ Files suitable and parameters suggest to choose for each model

| **Data File Name** | **Suitable Model**       | **Suggested Parameters** | **Has Header?** |
|---------------------|--------------------------|---------------------------|------------------|
| `data_10.csv`       | Linear Regression model | Fast, 1 (the index column)| Yes              |
| `wdbc.csv`          | SVM model               | Fast, 1 (the index column)| Yes              |
| `wdbc.csv`          | K-means model           | Fast, 1 (the index column)| Yes              |

### 🔑 Accounts Prepared for Testing

| **Account** | **Password** |
|-------------|--------------|
| test        | password     |
| karen       | password     |
| admin       | password     |

---

## 🧪 Instructions for Running Tests

### ✅ Unit Test

You can run unit tests directly from the terminal.

#### 🧭 Steps:

1. Open a terminal.

2. Navigate to the unit test folder:
```bash
cd app/unit_test
```
For Windows:
```bash
cd .\app
cd .\unit_test 
```

3. List available test files:
```bash
ls
```

4. Run a test file (e.g., `LinearRegression_test.py`):
```bash
python3 ./LinearRegression_test.py
```
For Windows:
```bash
python .\LinearRegression_test.py
```

5. Expected output when tests pass (Example):
```
Ran 3 tests in 0.002s
OK
```

✅ This means all tests in the file executed and passed successfully.



---

### 🧪 Selenium Test (Browser-based)

This test simulates real user interactions using the Selenium framework.

#### 🔧 Setup for macOS:

1. Install required Python packages:
```bash
pip install selenium flask
```

2. Install ChromeDriver using Homebrew:
```bash
brew install chromedriver
```
For Windows:
```bash
pip install webdriver-manager
```

3. Add your project root to `PYTHONPATH` (for macOS):
```bash
export PYTHONPATH=$PWD
```
💡 This tells Python to treat the current directory as a top-level package.

For Windows:
```bash
cd .\tests
```

4. Activate your virtual environment:
```bash
source myvenv/bin/activate
```

---

#### ▶️ Run the Selenium Test

Execute the following command:
```bash
python3 tests/selenium_test.py
```

Expected output example:
```
✅ User 'user1' created in test database.
URL after login submit: http://127.0.0.1:5000/dashboard/1
.
----------------------------------------------------------------------
Ran 1 test in 9.492s

OK
```

✅ This confirms that the Selenium test completed successfully and the app behaves as expected.

---


## 📚 References

OpenAI. (2024). *GPT-4o (ChatGPT, May 2024 version)* [Large language model]. https://chat.openai.com/

Alibaba Cloud. (2024). *Qwen: Large Language Model* [Language model family]. https://github.com/QwenLM/Qwen