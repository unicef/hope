from graphql import GraphQLError


class DataChangeValidator:
    @classmethod
    def verify_approve_data(cls, approve_data):
        if not isinstance(approve_data, dict):
            raise GraphQLError("Fields must be a dictionary with field name as key and boolean as a value")

        if not all([isinstance(value, bool) for value in approve_data.values()]):
            raise GraphQLError("Values must be booleans")

    @classmethod
    def verify_approve_data_against_object_data(cls, object_data, approve_data):
        error = "Provided fields are not the same as provided in the object approve data"
        if approve_data and not isinstance(object_data, dict):
            raise GraphQLError(error)

        approve_data_names = set(approve_data.keys())
        object_data_names = set(object_data.keys())
        if len(approve_data_names - object_data_names) != 0:
            raise GraphQLError(error)
