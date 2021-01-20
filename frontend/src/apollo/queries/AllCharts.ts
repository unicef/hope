import { gql } from 'apollo-boost';

export const Allcharts = gql`
  query AllCharts($businessAreaSlug: String!, $year: Int!) {
    chartProgrammesBySector(businessAreaSlug: $businessAreaSlug, year: $year) {
      labels
      datasets {
        label
        data
      }
    }
    chartPaymentVerification(businessAreaSlug: $businessAreaSlug, year: $year) {
      datasets {
        label
        data
      }
      labels
      households
    }
    chartVolumeByDeliveryMechanism(
      businessAreaSlug: $businessAreaSlug
      year: $year
    ) {
      datasets {
        data
      }
      labels
    }
    chartPayment(businessAreaSlug: $businessAreaSlug, year: $year) {
      datasets {
        data
      }
      labels
    }
    chartGrievances(businessAreaSlug: $businessAreaSlug, year: $year) {
      datasets {
        data
      }
      labels
      total
      totalDataChange
      totalSensitive
      totalComplaint
      totalNegativeFeedback
      totalReferral
      totalPositiveFeedback
    }
  }
`;
