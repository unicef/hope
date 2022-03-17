import React from 'react';
import { TargetPopulationHouseholdTable } from '../../containers/tables/targeting/TargetPopulationHouseholdTable';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../__generated__/graphql';
import { ApprovedTargetPopulationTable } from '../../containers/tables/targeting/TargetPopulation/ApprovedTargeting';
import { useBusinessArea } from '../../hooks/useBusinessArea';

export function TargetingHouseholds({
  status,
  id,
  canViewDetails,
}): React.ReactElement {
  const businessArea = useBusinessArea();

  let table;
  switch (status) {
    case 'DRAFT':
      table = (
        <TargetPopulationHouseholdTable
          id={id}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queryObjectName='candidateHouseholdsListByTargetingCriteria'
          canViewDetails={canViewDetails}
          variables={{ businessArea }}
        />
      );
      break;
    case 'LOCKED':
      table = (
        <ApprovedTargetPopulationTable
          id={id}
          canViewDetails={canViewDetails}
          variables={{ businessArea }}
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
          variables={{ businessArea }}
        />
      );
      break;
  }
  return <>{table}</>;
}
