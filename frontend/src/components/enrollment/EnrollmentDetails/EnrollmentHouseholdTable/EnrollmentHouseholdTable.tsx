import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { TargetPopulationHouseholdTableRow } from '../../../../containers/tables/targeting/TargetPopulationHouseholdTable/TargetPopulationHouseholdRow';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { TableWrapper } from '../../../core/TableWrapper';
import { headCells } from './EnrollmentHouseholdTableHeadCells';

interface EnrollmentHouseholdTableProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  canViewDetails?: boolean;
}

export const EnrollmentHouseholdTable = ({
  id,
  query,
  queryObjectName,
  variables,
  canViewDetails,
}: EnrollmentHouseholdTableProps): ReactElement => {
  const { t } = useTranslation();
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
