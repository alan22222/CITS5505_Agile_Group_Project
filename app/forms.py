from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SelectModelForm(FlaskForm):
    user_id = HiddenField('User ID')
    model_type = SelectField(
        'Model Type',
        choices=[
            ('linear_regression', 'Linear Regression'),
            ('random_forest',     'Random Forest'),
            ('svm',               'SVM'),
        ],
        validators=[DataRequired()]
    )
    precision_mode = SelectField(
        'Precision Mode',
        choices=[
            ('low',    'Low'),
            ('medium', 'Medium'),
            ('high',   'High'),
        ],
        validators=[DataRequired()]
    )
    target_index = IntegerField(
        'Target Column Index',
        validators=[DataRequired(), NumberRange(min=0)],
        description='Input the target index（min value is 0）'
    )
    has_header = BooleanField('CSV has header?')
    submit = SubmitField('Run Model')
