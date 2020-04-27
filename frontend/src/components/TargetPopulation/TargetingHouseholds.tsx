import React from 'react';
import { TargetPopulationHouseholdTable } from '../../containers/tables/TargetPopulationHouseholdTable';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../__generated__/graphql';
import { SentTargetPopulationTable } from '../../containers/tables/TargetPopulation/SentProgrammePopulation';

export function TargetingHouseholds({ status, id, selectedTab }) {
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
    case 'FINALIZED':
      table = <SentTargetPopulationTable selectedTab={selectedTab} id={id} />;
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
