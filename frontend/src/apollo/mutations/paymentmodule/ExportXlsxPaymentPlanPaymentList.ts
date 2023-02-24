import { gql } from 'apollo-boost';
export const ExportXlsxPPList = gql`
  mutation ExportXlsxPPList($paymentPlanId: ID!) {
    exportXlsxPaymentPlanPaymentList(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
