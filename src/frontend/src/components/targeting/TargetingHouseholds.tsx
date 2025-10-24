import withErrorBoundary from '@components/core/withErrorBoundary';
import { TargetPopulationHouseholdTable } from '@containers/tables/targeting/TargetPopulationHouseholdTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

function TargetingHouseholds({ id, canViewDetails }): ReactElement {
  const { businessArea } = useBaseUrl();

  return (
    <TargetPopulationHouseholdTable
      id={id}
      canViewDetails={canViewDetails}
      variables={{ businessArea }}
    />
  );
}

export default withErrorBoundary(TargetingHouseholds, 'TargetingHouseholds');
