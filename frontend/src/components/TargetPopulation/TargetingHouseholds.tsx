import React from 'react';
import { TargetPopulationHouseholdTable } from '../../containers/tables/TargetPopulationHouseholdTable';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../__generated__/graphql';
import { SentTargetPopulationTable } from '../../containers/tables/TargetPopulation/SentTargeting';
import { ApprovedTargetPopulationTable } from '../../containers/tables/TargetPopulation/ApprovedTargeting';

export function TargetingHouseholds({
  status,
  id,
  selectedTab,
}): React.ReactElement {
  let table;
  switch (status) {
    case 'DRAFT':
      table = (
        <TargetPopulationHouseholdTable
          id={id}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queryObjectName='candidateHouseholdsListByTargetingCriteria'
        />
      );
      break;
    case 'APPROVED':
      table = (
        <ApprovedTargetPopulationTable id={id} selectedTab={selectedTab} />
      );
      break;
    case 'FINALIZED':
      table = <SentTargetPopulationTable id={id} selectedTab={selectedTab} />;
      break;
    default:
      table = (
        <TargetPopulationHouseholdTable
          id={id}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queryObjectName='candidateHouseholdsListByTargetingCriteria'
        />
      );
      break;
  }
  return <>{table}</>;
}
