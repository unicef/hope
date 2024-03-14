import { gql } from '@apollo/client';

export const ExportXlsxPPListPerFsp = gql`
  mutation ExportXlsxPPListPerFsp($paymentPlanId: ID!) {
    exportXlsxPaymentPlanPaymentListPerFsp(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
        backgroundActionStatus
      }
    }
  }
`;
