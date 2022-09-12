import { gql } from 'apollo-boost';

export const PAYMENT_PLAN_QUERY = gql`
  query PaymentPlan($paymentPlanId: ID!) {
    paymentPlan(id: $paymentPlanId) {
      id
      unicefId
      status
      createdBy {
        id
        firstName
        lastName
        email
      }
      program {
        id
        name
      }
      targetPopulation {
        id
        name
      }
      currency
      currencyName
      startDate
      endDate
      dispersionStartDate
      dispersionEndDate
      femaleChildrenCount
      femaleAdultsCount
      maleChildrenCount
      maleAdultsCount
      totalHouseholdsCount
      totalIndividualsCount
      totalEntitledQuantity
      totalDeliveredQuantity
      totalUndeliveredQuantity
      approvalProcess {
        totalCount
        edgeCount
        edges {
          node {
            id
            sentForApprovalBy {
              id
              firstName
              lastName
              email
            }
            sentForApprovalDate
            sentForAuthorizationBy {
              id
              firstName
              lastName
              email
            }
            sentForAuthorizationDate
            sentForFinanceReviewBy {
              id
              firstName
              lastName
              email
            }
            sentForFinanceReviewDate
            actions {
              approval {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              authorization {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              financeReview {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              reject {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
            }
            rejectedOn
          }
        }
      }
      approvalNumberRequired
      authorizationNumberRequired
      financeReviewNumberRequired
      steficonRule {
        id
        rule {
          id
          name
        }
      }
      hasPaymentListXlsxFile
      xlsxFileImportedDate
      importedXlsxFileName
      totalEntitledQuantityUsd
      paymentsConflictsCount
      deliveryMechanisms {
        id
        name
        fsp {
          id
          name
        }
      }
      volumeByDeliveryMechanism {
        deliveryMechanism {
          id
          name
          order
          fsp {
            id
            name
          }
        }
        volume
        volumeUsd
      }
      hasPaymentListPerFspZipFile
      availableFspsForDeliveryMechanisms {
        deliveryMechanism
        fsps {
          id
          name
        }
      }
    }
  }
`;