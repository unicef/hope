---
title: Payment Module
tags:
    - Payment Planner
    - Target Population
    - Entitlements
---

# Payment Module

The Payment module is the payment management tool within HOPE that facilitates the creation of payment lists using information from targeted households. This module is used to create payment plans with payees and entitlements, track approvals and authorizations, create and export payment lists for payment providers (FSPs or IPs) and perform reconciliation with reports from payment providers.

## HOPE and VISION Integration

When payments are provided through an Implementing Partner and are included in the Direct Cash transfer to the Implementing Partner, HOPE Payment Module currently does not fetch data from Vision. It is the responsibility of UNICEF programme manager to ensure that the cash to be transferred to beneficiary by the IP in the Cash Plan does not exceed the agreed DCT amount. Cash plans using a UNICEF FSP need to receive up-to-date financial data (approved with sufficient fund commitments) from Vision to be approved and released. Vision either provides,

1. Regular operation FC for payment when UNICEF has its own account with the FSP.
2. ezHACT functionality to be used when UNICEF pays through a FSP where UNICEF has no account.

## How to create a payment plan


1. Select the Payment Module tab and choose your payment cycle, then click on “CREATE PAYMENT PLAN” button.
    ![Image](_screenshots/payment/pay_17.png)

    ![Image](_screenshots/payment/pay_18.png)

2. Select the corresponding target plan and fill in the parameters for the payment plan (currency, dispersion start date and dispersion end date).
    ![Image](_screenshots/payment/pay_19.png)

3. Once you click save, a summary of the payment plan will be displayed for review before creation. This includes the payment plan ID, a summary of the payment plan parameters and payees list. You also have an option to exclude households from the payment plan by pasting a list of household IDs in the Exclude field (click CREATE to view the input box). You can also upload supporting documents by clicking the “UPLOAD FILE.”
    ![Image](_screenshots/payment/pay_20.png)

4. Two actions are available at this stage

    1. EDIT: to change the payment plan details.
    2. LOCK: locks the configuration of the payment plan and allows creation of an entitlement formula. Once you lock the payment plan, the status will change from OPEN to LOCKED

    ![Image](_screenshots/payment/pay_21.png)


## Entitlement Formula

The entitle formula is used to define the amount that a household or individual should receive based on programmatic criteria. In the Payment Module there two options for setting up entitlement formulas:

1. Manual setup: this involves downloading the payment list (EXPORT XLSX), filling in the corresponding payment values and uploading the payment list (UPLOAD FILE) back to HOPE.

2. Custom setup: this involves submitting entitlement formula requirements to the HOPE support team for backend configuration in the HOPE. Once configured in HOPE, the entitlement formula will be available for selection on the ‘Select Entitlement Formula’ dropdown box.

    ![Image](_screenshots/payment/pay_22.png)

3. Click on LOCK payment plan.
    ![Image](_screenshots/payment/pay_23.png)

4. Send the payment plan for approval.
    ![Image](_screenshots/payment/pay_24.png)

5. Click “APPROVAL”, “AUTHORIZATION” to approve and authorize the payment plan.
    ![Image](_screenshots/payment/pay_25.png)

6. Click “DOWNLOAD XLSX” on the upper right.
    ![Image](_screenshots/payment/pay_26.png)

7. Fill out the column of DELIVERED QUANTITY in the excel that was downloaded in the previous step.
    ![Image](_screenshots/payment/pay_27.png)

8. Upload the filled excel through UPLOAD RECONCILIATION INFO.
    ![Image](_screenshots/payment/pay_28.png)

9. Click EXPORT XLSX on the upper right.
    ![Image](_screenshots/payment/pay_29.png)
