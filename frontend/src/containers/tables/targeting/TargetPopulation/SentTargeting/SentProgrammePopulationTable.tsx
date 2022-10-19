import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useTargetPopulationHouseholdsQuery } from '../../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../../hooks/useBusinessArea';
import { UniversalTable } from '../../../UniversalTable';
import { TableWrapper } from '../../../../../components/core/TableWrapper';
import { ProgrammeTableRow } from './ProgrammeTableRow';
import { headCells as programmeHeadCells } from './ProgrammeHeadCells';
import { headCells as targetPopulationHeadCells } from './TargetPopulationHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationTableRow';

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  selectedTab: number;
  canViewDetails?: boolean;
}

export const SentTargetPopulationTable = ({
  id,
  variables,
  selectedTab,
  canViewDetails,
}: TargetPopulationHouseholdProps): ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title={t('Households')}
        headCells={
          selectedTab === 0 ? programmeHeadCells : targetPopulationHeadCells
        }
        rowsPerPageOptions={[10, 15, 20]}
        query={useTargetPopulationHouseholdsQuery}
        queriedObjectName='targetPopulationHouseholdsQuery'
        initialVariables={initialVariables}
        renderRow={(row) => {
          return selectedTab === 0 ? (
            <ProgrammeTableRow
              key={row.name}
              household={row}
              canViewDetails={canViewDetails}
            />
          ) : (
            <TargetPopulationHouseholdTableRow
              key={row.name}
              household={row}
              canViewDetails={canViewDetails}
            />
          );
        }}
      />
    </TableWrapper>
  );
};
