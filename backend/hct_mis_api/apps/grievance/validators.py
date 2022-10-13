from hct_mis_api.apps.utils.exceptions import log_and_raise


class DataChangeValidator:
    @classmethod
    def verify_approve_data(cls, approve_data):
        if not isinstance(approve_data, dict):
            log_and_raise("Fields must be a dictionary with field name as key and boolean as a value")

        if not all([isinstance(value, bool) for value in approve_data.values()]):
            log_and_raise("Values must be booleans")

    @classmethod
    def verify_approve_data_against_object_data(cls, object_data, approve_data):
        error = "Provided fields are not the same as provided in the object approve data"
        if approve_data and not isinstance(object_data, dict):
            log_and_raise(error)

        approve_data_names = set(approve_data.keys())
        object_data_names = set(object_data.keys())
        if not approve_data_names.issubset(object_data_names):
            log_and_raise(error)
