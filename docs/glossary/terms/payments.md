---
description: ""
template: term.html
title: Payments
terms:
  - glossary:
    - Cash Plan
    - Fund Commitment
    - Fund reservation
    - Payment Instructions
    - "Payment Plan#Payment Plan"
    - "Payment Record#Payment Record"
    - Payment Verification
    - Payment Gateway
    - Purchase Order
    - Financial Service Provider
    - FSP
    - Top-Up
    - Top-Up Amendment

anchors:
    - "Payment Record": single entry in a Payment Plan

---


## Cash Plan

## Fund Commitment

## Fund Reservation

## Payment Instructions

The delivery channels that will be used for payment plan dispersion

## Payment Plan

List of <glossary:Payment Record>


!!! note

    - Target Population and Payment Plan is the same object in different phases of its life cycle
    - HouseHold Selection and Payment Record is the same object in different phases of its life cycle

## Payment Record

Single entry of a <glossary:Payment Plan> containing informations about Household and relative amounts

## Payment Verification

## Payment Gateway

A dedicated portal for managing payment operations. It transmits payment records to API-integrated Financial Service Providers (FSPs) and receives payment confirmation notifications in real-time.

## Purchase Order

## Financial Service Provider

These providers are the ones make the final payments to beneficiaries.

## Delivery Type

Deposit to card, transfer or cash

## Distribution Modality

Grouping of assistance measurement (currency), delivery type, entitlement formula and FSP

## Distribution Level

## Payment Gateway

The component that is used to manage API-integrated FSPs and their corresponding payment records.

## Top-Up

An additional <glossary:Payment Plan> created from a Standard plan in Accepted or Finished status, paying selected beneficiaries of that plan again. The amount is decided at creation: one fixed value for every eligible beneficiary, or per beneficiary from an uploaded template. One Top-Up per beneficiary per source plan.

## Top-Up Amendment

A correction layer created from a <glossary:Top-Up> in Accepted or Finished status, funded the same two ways as the Top-Up itself. One Amendment per beneficiary per source Top-Up; an Amendment cannot be amended again.
