import React from 'react';
import { TargetPopulationHouseholdTable } from '../../containers/tables/targeting/TargetPopulationHouseholdTable';
import { useTargetPopulationHouseholdsQuery } from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';

export function TargetingHouseholds({
  id,
  canViewDetails,
}): React.ReactElement {
  const businessArea = useBusinessArea();

  return (
    <TargetPopulationHouseholdTable
      id={id}
      query={useTargetPopulationHouseholdsQuery}
      queryObjectName='targetPopulationHouseholds'
      canViewDetails={canViewDetails}
      variables={{ businessArea }}
    />
  );
}
