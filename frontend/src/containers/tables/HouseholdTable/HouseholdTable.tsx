import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  HouseholdNode,
  useAllHouseholdsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './HouseholdTableHeadCells';
import { HouseHoldTableRow } from './HouseholdTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

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
    familySize: JSON.stringify(filter.householdSize),
    search: filter.text,
    adminArea: filter.adminArea?.node?.id,
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
        query={useAllHouseholdsQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
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
