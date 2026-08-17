"""
Move USDC wallet number images off Individual.flex_fields onto the wallet account.

The image belongs to the wallet, not to the individual, so every ``wallet_num_image_i_f``
flex value is copied to an AccountAttachment on that individual's digital wallet account and
the flex key is dropped. The source file is left in storage; only the flex key is removed.

Run from Django shell:
    from hope.one_time_scripts.migrate_wallet_images_to_account_attachments import (
        migrate_wallet_images_to_account_attachments,
    )
    migrate_wallet_images_to_account_attachments()
"""

from django.core.files.storage import default_storage
from django.db import transaction

from hope.models import Account, AccountAttachment, DeliveryMechanism, Individual

WALLET_NUMBER_IMAGE_FIELD = "wallet_num_image_i_f"
WALLET_NUMBER_IMAGE_TITLE = "Wallet number image"
DIGITAL_WALLET_DELIVERY_MECHANISM_CODE = "transfer_to_digital_wallet"


def migrate_wallet_images_to_account_attachments() -> None:
    delivery_mechanism = DeliveryMechanism.objects.filter(code=DIGITAL_WALLET_DELIVERY_MECHANISM_CODE).first()
    if not delivery_mechanism or not delivery_mechanism.account_type_id:
        print(f"Delivery mechanism '{DIGITAL_WALLET_DELIVERY_MECHANISM_CODE}' has no account type.")
        return

    individuals = Individual.all_objects.filter(flex_fields__has_key=WALLET_NUMBER_IMAGE_FIELD).only(
        "id", "flex_fields"
    )
    migrated = skipped = failed = 0

    for individual in individuals.iterator(chunk_size=500):
        source_name = individual.flex_fields.get(WALLET_NUMBER_IMAGE_FIELD)
        account = Account.all_objects.filter(
            individual_id=individual.pk, account_type_id=delivery_mechanism.account_type_id
        ).first()

        if not account:
            print(f"[SKIP] {individual.pk}: no digital wallet account, flex field left untouched")
            skipped += 1
            continue
        if not source_name or not default_storage.exists(source_name):
            print(f"[SKIP] {individual.pk}: source file '{source_name}' missing from storage")
            skipped += 1
            continue
        if AccountAttachment.objects.filter(account=account, title=WALLET_NUMBER_IMAGE_TITLE).exists():
            _drop_flex_field(individual)
            print(f"[SKIP] {individual.pk}: attachment already exists, flex field dropped")
            skipped += 1
            continue

        try:
            with default_storage.open(source_name) as source:
                copied_name = default_storage.save(source_name, source)
        except Exception as e:  # noqa: BLE001 - one bad blob must not stop the run
            print(f"[ERROR] {individual.pk}: failed to copy '{source_name}': {e}")
            failed += 1
            continue

        with transaction.atomic():
            AccountAttachment.objects.create(account=account, title=WALLET_NUMBER_IMAGE_TITLE, file=copied_name)
            _drop_flex_field(individual)
        migrated += 1

    print(f"Done. migrated={migrated} skipped={skipped} failed={failed}")


def _drop_flex_field(individual: Individual) -> None:
    del individual.flex_fields[WALLET_NUMBER_IMAGE_FIELD]
    individual.save(update_fields=["flex_fields"])
