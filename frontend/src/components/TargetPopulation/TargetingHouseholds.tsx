import React from 'react';
import { TargetPopulationHouseholdTable } from '../../containers/tables/TargetPopulationHouseholdTable';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../__generated__/graphql';
import { ApprovedTargetPopulationTable } from '../../containers/tables/TargetPopulation/ApprovedTargeting';

export function TargetingHouseholds({
  status,
  id,
  canViewDetails,
}): React.ReactElement {
  let table;
  switch (status) {
    case 'DRAFT':
      table = (
        <TargetPopulationHouseholdTable
          id={id}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queryObjectName='candidateHouseholdsListByTargetingCriteria'
          canViewDetails={canViewDetails}
        />
      );
      break;
    case 'APPROVED':
      table = (
        <ApprovedTargetPopulationTable
          id={id}
          canViewDetails={canViewDetails}
        />
      );
      break;
    default:
      table = (
        <TargetPopulationHouseholdTable
          id={id}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queryObjectName='candidateHouseholdsListByTargetingCriteria'
          canViewDetails={canViewDetails}
        />
      );
      break;
  }
  return <>{table}</>;
}
