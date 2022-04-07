def get_records_alexis():
    from hct_mis_api.apps.registration_datahub.models import Record
    import json

    records = Record.objects.all()[300:302]
    data_for_alexis = []
    data_for_alexis.append(
        (
            "full_name_i_c",
            "tax_id_no_i_c",
            "bank_account_h_f",
            "bank_name_h_f",
            "other_bank_name",
            "bank_account",
            "bank_account_number",
            "debit_card_number_h_f",
            "debit_card_number",
        )
    )
    for record in records:
        try:
            individuals = json.loads(record.storage.tobytes().decode("utf-8")).get("individuals")
            if not individuals:
                continue
            data = individuals[0]
            full_name = f"{data.get('given_name_i_c')} {data.get('family_name_i_c')}"
            data_for_alexis.append(
                (
                    full_name,
                    data.get("tax_id_no_i_c", ""),
                    data.get("bank_account_h_f", ""),
                    data.get("bank_name_h_f", ""),
                    data.get("other_bank_name", ""),
                    data.get("bank_account", ""),
                    data.get("bank_account_number", ""),
                    data.get("debit_card_number_h_f", ""),
                    data.get("debit_card_number", ""),
                )
            )
        except:
            raise
    with open("data.csv", "a") as f:
        for row in data_for_alexis:
            f.write(",".join(map(str, row))+"\n")
