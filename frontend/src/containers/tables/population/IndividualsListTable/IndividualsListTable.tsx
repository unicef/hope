import React from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import {
  IndividualNode,
  AllIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  useAllIndividualsForPopulationTableQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';

interface IndividualsListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
  choicesData: HouseholdChoiceDataQuery;
}

export const IndividualsListTable = ({
  businessArea,
  filter,
  canViewDetails,
  choicesData,
}: IndividualsListTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables = {
    age: JSON.stringify({ min: filter.ageMin, max: filter.ageMax }),
    businessArea,
    sex: [filter.sex],
    search: filter.search,
    admin2: [filter.admin2],
    flags: filter.flags,
    status: filter.status,
    lastRegistrationDate: JSON.stringify({
      min: filter.lastRegistrationDateMin,
      max: filter.lastRegistrationDateMax,
    }),
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        title={t('Individuals')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllIndividualsForPopulationTableQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        allowSort={false}
        filterOrderBy={filter.orderBy}
        renderRow={(row) => (
          <IndividualsListTableRow
            key={row.id}
            individual={row}
            canViewDetails={canViewDetails}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
};
