import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './TargetPopulationHouseholdHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationHouseholdRow';

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  canViewDetails?: boolean;
}

export const TargetPopulationHouseholdTable = ({
  id,
  query,
  queryObjectName,
  variables,
  canViewDetails,
}: TargetPopulationHouseholdProps): ReactElement => {
  const { t } = useTranslation();
  console.log('variables', variables);
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title={t('Households')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={query}
        queriedObjectName={queryObjectName}
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationHouseholdTableRow
            key={row.id}
            household={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
