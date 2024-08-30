import { gql } from '@apollo/client';

export const AllTargetPopulations = gql`
  query AllTargetPopulations(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $status: String
    $totalHouseholdsCountMin: Int
    $totalHouseholdsCountMax: Int
    $businessArea: String
    $program: [ID]
    $programCycle: String
    $createdAtRange: String
    $paymentPlanApplicable: Boolean
  ) {
    allTargetPopulation(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      status: $status
      totalHouseholdsCountMin: $totalHouseholdsCountMin
      totalHouseholdsCountMax: $totalHouseholdsCountMax
      businessArea: $businessArea
      program: $program
      programCycle: $programCycle
      createdAtRange: $createdAtRange
      paymentPlanApplicable: $paymentPlanApplicable
    ) {
      edges {
        node {
          ...targetPopulationMinimal
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
