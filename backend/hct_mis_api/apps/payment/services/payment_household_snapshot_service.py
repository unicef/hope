

excluded_individual_fields = [

]
excluded_household_fields = [

]


def create_payment_snapshot_data(household):
    household_data={}
    all_household_data_dict = household.__dict__
    keys = [key for key in all_household_data_dict.keys() if key not in excluded_household_fields]
    household_data['individuals'] = []
    all_household_data_dict['roles'] = []
    for key in keys:
        household_data[key] = all_household_data_dict[key]
    for individual in household.individuals.all():
        household_data['individuals'].append(get_individual_snapshot(individual))
    for role in household.individuals_and_roles.all():
        all_household_data_dict['roles'].append({
            'role': role.role,
            'individual': get_individual_snapshot(role.individual)
        })


def get_individual_snapshot(individual):
    all_individual_data_dict = individual.__dict__
    keys = [key for key in all_individual_data_dict.keys() if key not in excluded_individual_fields]
    individual_data = {}
    for key in keys:
        individual_data[key] = all_individual_data_dict[key]
    individual_data['documents'] = []
    for document in individual.documents.all():
        document_data = {
            'document_type': document.document_type,
            'document_number': document.document_number,
            'document_expiry_date': document.document_expiry_date,
            'document_issuing_country': document.document_issuing_country,
        }
        individual_data['documents'].append(document_data)
    return individual_data


