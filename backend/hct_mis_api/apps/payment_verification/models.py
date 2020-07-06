class CashPlanPaymentVerification(models.Model):
    cash_plan = fk(CashPlan)
    status = 
    rapid_pro_payment_verification_flow_id = models.CharField(blank=True)
    archived = BooleanField(help_text="Only one should be active at any given time")


class PaymentRecordVerification(models.Model):
    cp_pv = fk(CashPlanPaymentVerification)
    payment_record = fk(PaymentRecrd)
    did_you_receive = BooleanField()
    amount_received = DecimalField()
