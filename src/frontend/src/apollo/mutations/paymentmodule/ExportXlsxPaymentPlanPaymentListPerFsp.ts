import { gql } from '@apollo/client';

export const ExportXlsxPPListPerFsp = gql`
  mutation ExportXlsxPPListPerFsp($paymentPlanId: ID!, $fspXlsxTemplateId: ID) {
    exportXlsxPaymentPlanPaymentListPerFsp(
      paymentPlanId: $paymentPlanId
      fspXlsxTemplateId: $fspXlsxTemplateId
    ) {
      paymentPlan {
        id
        status
        backgroundActionStatus
      }
    }
  }
`;
