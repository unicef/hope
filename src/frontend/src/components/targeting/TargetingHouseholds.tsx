import { TargetPopulationHouseholdTable } from '@containers/tables/targeting/TargetPopulationHouseholdTable';
import { useAllPaymentsForTableQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

export function TargetingHouseholds({ id, canViewDetails }): ReactElement {
  const { businessArea } = useBaseUrl();

  return (
    <TargetPopulationHouseholdTable
      id={id}
      query={useAllPaymentsForTableQuery}
      queryObjectName="allPayments"
      canViewDetails={canViewDetails}
      variables={{ businessArea }}
    />
  );
}
