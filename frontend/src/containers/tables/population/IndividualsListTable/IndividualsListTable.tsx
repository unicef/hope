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
  filterOrderBy: string;
}

export const IndividualsListTable = ({
  businessArea,
  filter,
  canViewDetails,
  choicesData,
  filterOrderBy,
}: IndividualsListTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables = {
    age: JSON.stringify(filter.age),
    businessArea,
    sex: [filter.sex],
    search: filter.text,
    adminArea: filter.adminArea?.node?.id,
    flags: filter.flags,
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
        filterOrderBy={filterOrderBy}
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
