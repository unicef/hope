import { gql } from '@apollo/client';

export const UPDATE_PAYMENT_PLAN = gql`
  mutation UpdatePP(
    $paymentPlanId: ID!
    $dispersionStartDate: Date
    $dispersionEndDate: Date
    $currency: String
    $name: String
    $targetingCriteria: TargetingCriteriaObjectType
    $programCycleId: ID
    $vulnerabilityScoreMin: Decimal
    $vulnerabilityScoreMax: Decimal
    $excludedIds: String
    $exclusionReason: String
    $fspId: ID
    $deliveryMechanismCode: String
  ) {
    updatePaymentPlan(
      input: {
        paymentPlanId: $paymentPlanId
        dispersionStartDate: $dispersionStartDate
        dispersionEndDate: $dispersionEndDate
        currency: $currency
        name: $name
        targetingCriteria: $targetingCriteria
        programCycleId: $programCycleId
        vulnerabilityScoreMin: $vulnerabilityScoreMin
        vulnerabilityScoreMax: $vulnerabilityScoreMax
        excludedIds: $excludedIds
        exclusionReason: $exclusionReason
        fspId: $fspId
        deliveryMechanismCode: $deliveryMechanismCode
      }
    ) {
      paymentPlan {
        id
      }
    }
  }
`;
