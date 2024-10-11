import * as React from 'react';
import { TargetPopulationHouseholdTable } from '@containers/tables/targeting/TargetPopulationHouseholdTable';
import { useTargetPopulationHouseholdsQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

export function TargetingHouseholds({
  id,
  canViewDetails,
}): React.ReactElement {
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
