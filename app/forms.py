from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, IntegerField, SelectField,
                     SubmitField)
from wtforms.validators import DataRequired, NumberRange


class SelectModelForm(FlaskForm):
    user_id = HiddenField('User ID')
    model_type = SelectField(
        'Model Type',
        choices=[
            ('linear_regression', 'Linear Regression'),
            ('KMeans',     'K-means'),
            ('SVM',               'SVM'),
        ],
        validators=[DataRequired()]
    )
    precision_mode = SelectField(
        'Precision Mode',
        choices=[
            ('Fast',    'Fast'),
            ('Balance', 'Balance'),
            ('High Precision',   'High Precision'),
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
