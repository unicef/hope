import { TargetPopulationHouseholdTable } from '@containers/tables/targeting/TargetPopulationHouseholdTable';
import { useTargetPopulationHouseholdsQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

export function TargetingHouseholds({ id, canViewDetails }): ReactElement {
  const { businessArea } = useBaseUrl();

  return (
    <TargetPopulationHouseholdTable
      id={id}
      query={useTargetPopulationHouseholdsQuery}
      queryObjectName="targetPopulationHouseholds"
      canViewDetails={canViewDetails}
      variables={{ businessArea }}
    />
  );
}
