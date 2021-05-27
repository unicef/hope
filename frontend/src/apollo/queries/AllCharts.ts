import {gql} from 'apollo-boost';

export const Allcharts = gql`
  query AllCharts(
    $businessAreaSlug: String!
    $year: Int!
    $program: String
    $administrativeArea: String
  ) {
    chartProgrammesBySector(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      labels
      datasets {
        label
        data
      }
    }
    chartPaymentVerification(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        label
        data
      }
      labels
      households
      averageSampleSize
    }
    chartVolumeByDeliveryMechanism(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
      }
      labels
    }
    chartPayment(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
      }
      labels
    }
    chartGrievances(
      businessAreaSlug: $businessAreaSlug
      year: $year
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
      }
      labels
      totalNumberOfGrievances
      totalNumberOfFeedback
      totalNumberOfOpenSensitive
    }
    sectionHouseholdsReached(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      total
    }
    sectionIndividualsReached(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      total
    }
    sectionChildReached(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      total
    }

    chartIndividualsReachedByAgeAndGender(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
      }
      labels
    }
    chartIndividualsWithDisabilityReachedByAge(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
        label
      }
      labels
    }
    sectionTotalTransferred(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      total
    }
    chartTotalTransferredByMonth(
      businessAreaSlug: $businessAreaSlug
      year: $year
      program: $program
      administrativeArea: $administrativeArea
    ) {
      datasets {
        data
        label
      }
      labels
    }
  }
`;
