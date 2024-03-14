import { gql } from '@apollo/client';

export const EXPORT_PDF_PP_SUMMARY = gql`
  mutation exportPdfPPSummary($paymentPlanId: ID!) {
    exportPdfPaymentPlanSummary(paymentPlanId: $paymentPlanId) {
      paymentPlan {
        id
      }
    }
  }
`;
