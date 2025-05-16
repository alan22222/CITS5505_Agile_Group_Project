# 🚀 OneClickML – CITS5505 Agile Group Project

## 👥 Group 39 Members

| **UWA ID** | **Name**       | **GitHub Username(s)**       |
|------------|----------------|------------------------------|
| 24085576   | Alan Chacko    | alan22222                    |
| 24239318   | Ayden Pan      | Pixy-greenhand               |
| 24302286   | Yee Man Tsai   | ym-Tsai                      |
| 24256987   | Yanchen Yu     | wizardG7777777, Yanchen Yu   |

---

## 🎯 About OneClickML

**OneClickML** is a user-friendly machine learning platform that helps users quickly discover the best model for their dataset — with just one click.

### 🔍 Key Features
- Easy registration and login
- CSV upload and validation
- One-click ML model execution
- Configurable processing speed
- Dashboard with visual insights
- AI analysis for the results

### 🧠 Supported ML Models
- Linear Regression
- Support Vector Machine (SVM)
- K-Means Clustering

---

## ⚙️ How to Run OneClickML

OneClickML is built with **Flask**, **SQLAlchemy**, and **Python 3.10**.

### 🗂️ Folder Setup
1. Unzip the project folder.
2. Open Terminal (macOS) or PowerShell (Windows).

### 🛠️ Installation

1. Clone the repository:
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

4. Initialize the database (first-time setup only)::
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

6. Visit in your browser:
```
http://127.0.0.1:5000
```

---

### ⚠️ Python Version Compatibility Tip

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
| `data_10.csv`       | Linear Regression model | Fast, Index1| Yes              |
| `wdbc.csv`          | SVM model               | Fast, Index1| Yes              |
| `wdbc.csv`          | K-means model           | Fast, Index1| Yes              |

### 🔑 Test Accounts

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

1. Open terminal.

2. Navigate to the unit test folder. 
For macOS:
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

4. Run a test file (e.g., `LinearRegression_test.py`). 
For macOS:
```bash
python3 ./LinearRegression_test.py
```
For Windows:
```bash
python .\LinearRegression_test.py
```

5. Expected output when the tests pass (Example):
```
Ran 4 tests in 40.894s

OK
```

✅ This means all tests in the file executed and passed successfully.



---

### 🧪 Selenium Test (Browser-based)

This test simulates real user interactions using the Selenium framework.

#### 🔧 Setup:

1. Ensure you have install the dependencies. The `selenium` is a must for running selenium tests.
```bash
pip install -r requirements.txt
```

2. Install ChromeDriver manager. 
For macOS via Homebrew:
```bash
brew install chromedriver
```
For Windows:
```bash
pip install chromedriver
```

3. Ensure you are at the correct path, which is the root.
For macOS, you can add your project root to `PYTHONPATH`:
```bash
export PYTHONPATH=$PWD
```
💡 This tells Python to treat the current directory as a top-level package.

---

#### ▶️ Run the Selenium Test

For macOS, execute the following command:
```bash
python tests/test_e2e.py
```

For Windows:
```bash
python -m unittest tests/test_e2e.py
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

- OpenAI. (2024). *GPT-4o (ChatGPT, May 2024 version)* . https://chat.openai.com/

- Alibaba Cloud. (2024). *Qwen: Large Language Model* . https://github.com/QwenLM/Qwen