# ~*~ coding: utf-8 ~*~


class CarrierValidationException(Exception):
    pass


class Base(object):
    customer_info_spec = None
    data = None

    def create_document(self):
        document = ''.join(self.data)
        return document

    def validate(self):
        # TODO: EG - check and see if we are validating the size of the string
        # vs the amount allowed and messaging that out to thec consumer.
        if not self.customer_info_spec:
            raise CarrierValidationException(
                'Failed to setup customer spec values')
        # Do some validation stuff here...
        # for key, value in self.payload.items():
        for validator in self.customer_info_spec:
            key, value_type, value_length, value_position = validator
            special = validator[4] if len(validator) > 4 else None
            value_spec = {
                'special': special,
                'value_length': value_length,
                'value_position': value_position
            }

            try:
                value = self.payload.get(key)
                if key != 'filler' and not isinstance(value, value_type) or\
                        len(str(value)) > value_length:
                    raise MetLifeCarrierValidationException(
                        'Failed to validate `{}`, value given: `{}` of type: `{}` and expecting of type `{}`'
                        .format(key, value, type(value), value_type))
            except Exception as e:
                if not self.errors:
                    self.errors = []
                self.errors.append(str(e))
            if key == 'filler':
                value = ' ' * value_length
            self.add_to_data(key, value, value_spec)
        if self.errors:
            raise CarrierValidationException('{}'.format(str(self.errors)))

    def add_to_data(self, key, value, value_spec):
        if not self.data:
            self.data = []
        if not value:
            value = ' ' * value_spec.get('value_length')
        elif len(str(value)) != value_spec.get('value_length'):
            value = '{}{}'.format(
                value, (' ' * (value_spec.get('value_length') - len(str(value)))))
        self.data.append(str(value))


class MetLifeCarrierValidationException(Exception):
    pass


class MetLifeCarrier(Base):
    document = None
    errors = None
    # key, type, length, position, special treatment
    customer_info_spec = [
        ('transaction_code', str, 1, 1,),
        ('customer_number', int, 7, 2,),
        ('employee_number', int, 11, 9,),
        ('filler', str, 11, 20,),
        ('ssn', int, 9, 31,),
        ('last_name', str, 20, 40,),
        ('first_name', str, 12, 60,),
        ('middle_initial', str, 1, 72,),
        ('dob', int, 8, 73,),
        ('marital_status', str, 1, 81,),
        ('gender', str, 1, 82,),
        ('relationship', int, 2, 83,),
        ('doh', int, 8, 85,),
        ('identification', int, 11, 93,),
        ('smoker_code', str, 1, 104,),
        ('spouse_smoker_code', str, 1, 105,),
        ('filler', str, 22, 106,),
        ('survivor_indicator', str, 1, 128,),
        ('survivor_ssn', int, 9, 129,),
        ('survivor_last_name', str, 20, 138,),
        ('survivor_first_name', str, 12, 158,),
        ('foreign_address_indicator', str, 1, 170,),
        ('care_of_address', str, 32, 171,),
        ('address', str, 32, 203,),
        ('city', str, 21, 235,),
        ('state', str, 2, 256,),
        ('postal_code', int, 9, 258,)
    ]

    def __init__(self, payload):
        self.payload = payload
        self.validate()
        self.document = self.create_document()


class OOMCarrier(Base):
    pass


class LibertyMutualCarrier(Base):
    pass
