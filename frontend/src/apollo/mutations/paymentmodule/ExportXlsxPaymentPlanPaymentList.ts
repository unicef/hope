import { gql } from '@apollo/client';
export const ExportXlsxPPList = gql`
  mutation ExportXlsxPPList($paymentPlanId: ID!) {
    exportXlsxPaymentPlanPaymentList(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
        backgroundActionStatus
      }
    }
  }
`;
