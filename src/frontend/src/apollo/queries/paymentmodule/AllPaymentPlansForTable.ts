import { gql } from '@apollo/client';

export const AllPaymentPlansForTable = gql`
  query AllPaymentPlansForTable(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $businessArea: String!
    $search: String
    $status: [String]
    $totalEntitledQuantityFrom: Float
    $totalEntitledQuantityTo: Float
    $dispersionStartDate: Date
    $dispersionEndDate: Date
    $isFollowUp: Boolean
    $program: String
    $programCycle: String
    $totalHouseholdsCountWithValidPhoneNoMin: Int
    $totalHouseholdsCountWithValidPhoneNoMax: Int
    $createdAtRange: String
    $statusNot: String
    $isPaymentPlan: Boolean
    $isTargetPopulation: Boolean
    $verificationStatus: [String]
    $serviceProvider: String
    $deliveryTypes: [String]
    $startDate: Date
    $endDate: Date
  ) {
    allPaymentPlans(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
      search: $search
      status: $status
      totalEntitledQuantityFrom: $totalEntitledQuantityFrom
      totalEntitledQuantityTo: $totalEntitledQuantityTo
      dispersionStartDate: $dispersionStartDate
      dispersionEndDate: $dispersionEndDate
      isFollowUp: $isFollowUp
      program: $program
      programCycle: $programCycle
      totalHouseholdsCountWithValidPhoneNoMin: $totalHouseholdsCountWithValidPhoneNoMin
      totalHouseholdsCountWithValidPhoneNoMax: $totalHouseholdsCountWithValidPhoneNoMax
      createdAtRange: $createdAtRange
      statusNot: $statusNot
      isPaymentPlan: $isPaymentPlan
      isTargetPopulation: $isTargetPopulation
      verificationStatus: $verificationStatus
      serviceProvider: $serviceProvider
      deliveryTypes: $deliveryTypes
      startDate: $startDate
      endDate: $endDate
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          id
          unicefId
          name
          isFollowUp
          followUps {
            totalCount
            edges {
              node {
                id
                unicefId
                dispersionStartDate
                dispersionEndDate
              }
            }
          }
          status
          paymentVerificationSummary {
            status
          }
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
        }
      }
    }
  }
`;
