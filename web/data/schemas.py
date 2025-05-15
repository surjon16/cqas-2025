from marshmallow import Schema, fields, validates, ValidationError

# All classes declared will be used for validation

class CreateAccountSchema(Schema):
    
    first_name  = fields.Str(required=True)
    last_name   = fields.Str(required=True)
    password    = fields.Str(required=True)

    @validates('first_name')
    def validate_first_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your first name.')

    @validates('last_name')
    def validate_last_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your last name.')

    @validates('password')
    def validate_password(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide a password.')

class UpdateAccountSchema(Schema):
    
    first_name  = fields.Str(required=True)
    last_name   = fields.Str(required=True)
    role_id     = fields.Str(required=True)

    @validates('first_name')
    def validate_first_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your first name.')

    @validates('last_name')
    def validate_last_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your last name.')

    @validates('role_id')
    def validate_role_id(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide a role.')

class RegisterAccountSchema(Schema):

    first_name  = fields.Str(required=True)
    last_name   = fields.Str(required=True)
    email       = fields.Email(required=True)
    password    = fields.Str(required=True)

    @validates('first_name')
    def validate_first_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your first name.')

    @validates('last_name')
    def validate_last_name(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide your last name.')

    @validates('password')
    def validate_password(self, value):
        if value == '' or value is None:
            raise ValidationError('Please provide a password.')
