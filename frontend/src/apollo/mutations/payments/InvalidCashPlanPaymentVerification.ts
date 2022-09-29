import { gql } from 'apollo-boost';

export const InvalidPaymentVerificationPlan = gql`
  mutation InvalidPaymentVerificationPlan($paymentVerificationPlanId: ID!) {
    invalidPaymentVerificationPlan(
      paymentVerificationPlanId: $paymentVerificationPlanId
    ) {
      cashPlan {
        id
        # verificationPlans {
        #   edges {
        #     node {
        #       id
        #       xlsxFileExporting
        #       hasXlsxFile
        #       xlsxFileWasDownloaded
        #       xlsxFileImported
        #     }
        #   }
        # }
      }
    }
  }
`;
