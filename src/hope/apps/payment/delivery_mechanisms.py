from django.utils.translation import gettext_lazy as _


class DeliveryMechanismChoices:
    DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL = "Cardless cash withdrawal"
    DELIVERY_TYPE_CASH = "Cash"
    DELIVERY_TYPE_CASH_BY_FSP = "Cash by FSP"
    DELIVERY_TYPE_CHEQUE = "Cheque"
    DELIVERY_TYPE_DEPOSIT_TO_CARD = "Deposit to Card"
    DELIVERY_TYPE_MOBILE_MONEY = "Mobile Money"
    DELIVERY_TYPE_PRE_PAID_CARD = "Pre-paid card"
    DELIVERY_TYPE_REFERRAL = "Referral"
    DELIVERY_TYPE_TRANSFER = "Transfer"
    DELIVERY_TYPE_TRANSFER_TO_ACCOUNT = "Transfer to Account"
    DELIVERY_TYPE_VOUCHER = "Voucher"
    DELIVERY_TYPE_ATM_CARD = "ATM Card"
    DELIVERY_TYPE_CASH_OVER_THE_COUNTER = "Cash over the counter"
    DELIVERY_TYPE_TRANSFER_TO_DIGITAL_WALLET = "Transfer to Digital Wallet"

    DELIVERY_TYPES_IN_CASH = (
        DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL,
        DELIVERY_TYPE_CASH,
        DELIVERY_TYPE_CASH_BY_FSP,
        DELIVERY_TYPE_CHEQUE,
        DELIVERY_TYPE_DEPOSIT_TO_CARD,
        DELIVERY_TYPE_MOBILE_MONEY,
        DELIVERY_TYPE_PRE_PAID_CARD,
        DELIVERY_TYPE_REFERRAL,
        DELIVERY_TYPE_TRANSFER,
        DELIVERY_TYPE_TRANSFER_TO_ACCOUNT,
        DELIVERY_TYPE_ATM_CARD,
        DELIVERY_TYPE_CASH_OVER_THE_COUNTER,
        DELIVERY_TYPE_TRANSFER_TO_DIGITAL_WALLET,
    )
    DELIVERY_TYPES_IN_VOUCHER = (DELIVERY_TYPE_VOUCHER,)

    DELIVERY_TYPE_CHOICES = (
        (DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL, _("Cardless cash withdrawal")),
        (DELIVERY_TYPE_CASH, _("Cash")),
        (DELIVERY_TYPE_CASH_BY_FSP, _("Cash by FSP")),
        (DELIVERY_TYPE_CHEQUE, _("Cheque")),
        (DELIVERY_TYPE_DEPOSIT_TO_CARD, _("Deposit to Card")),
        (DELIVERY_TYPE_MOBILE_MONEY, _("Mobile Money")),
        (DELIVERY_TYPE_PRE_PAID_CARD, _("Pre-paid card")),
        (DELIVERY_TYPE_REFERRAL, _("Referral")),
        (DELIVERY_TYPE_TRANSFER, _("Transfer")),
        (DELIVERY_TYPE_TRANSFER_TO_ACCOUNT, _("Transfer to Account")),
        (DELIVERY_TYPE_VOUCHER, _("Voucher")),
        (DELIVERY_TYPE_ATM_CARD, _("ATM Card")),
        (DELIVERY_TYPE_CASH_OVER_THE_COUNTER, _("Cash over the counter")),
        (DELIVERY_TYPE_TRANSFER_TO_DIGITAL_WALLET, _("Transfer to Digital Wallet")),
    )
