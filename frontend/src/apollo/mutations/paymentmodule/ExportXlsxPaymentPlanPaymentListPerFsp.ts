import { gql } from 'apollo-boost';
export const ExportXlsxPPListPerFsp = gql`
  mutation ExportXlsxPPListPerFsp($paymentPlanId: ID!) {
    exportXlsxPaymentPlanPaymentListPerFsp(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
