import React from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import {
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  HouseholdNode,
  useAllHouseholdsForPopulationTableQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './HouseholdTableHeadCells';
import { HouseHoldTableRow } from './HouseholdTableRow';

interface HouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  canViewDetails: boolean;
}

export const HouseholdTable = ({
  businessArea,
  filter,
  choicesData,
  canViewDetails,
}: HouseholdTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify({
      min: filter.householdSizeMin,
      max: filter.householdSizeMax,
    }),
    search: filter.text,
    adminArea: filter.adminArea,
    residenceStatus: filter.residenceStatus,
  };
  if (filter.program) {
    initialVariables.programs = [filter.program];
  }

  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        title={t('Households')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllHouseholdsForPopulationTableQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        allowSort={false}
        filterOrderBy={filter.orderBy}
        renderRow={(row) => (
          <HouseHoldTableRow
            key={row.id}
            household={row}
            choicesData={choicesData}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
