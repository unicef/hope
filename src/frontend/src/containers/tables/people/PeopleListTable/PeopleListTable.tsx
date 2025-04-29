import { useTranslation } from 'react-i18next';
import {
  AllIndividualsForPopulationTableQueryVariables,
  IndividualRdiMergeStatus,
  useAllIndividualsForPopulationTableQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { dateToIsoString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './PeopleListTableHeadCells';
import { PeopleListTableRow } from './PeopleListTableRow';
import { ReactElement } from 'react';

interface PeopleListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export const PeopleListTable = ({
  businessArea,
  filter,
  canViewDetails,
}: PeopleListTableProps): ReactElement => {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const initialVariables: AllIndividualsForPopulationTableQueryVariables = {
    age: JSON.stringify({ min: filter.ageMin, max: filter.ageMax }),
    businessArea,
    sex: [filter.sex],
    search: filter.search.trim(),
    documentType: filter.documentType,
    documentNumber: filter.documentNumber.trim(),
    admin1: [filter.admin1],
    admin2: [filter.admin2],
    flags: filter.flags,
    status: filter.status,
    lastRegistrationDate: JSON.stringify({
      min: dateToIsoString(filter.lastRegistrationDateMin, 'startOfDay'),
      max: dateToIsoString(filter.lastRegistrationDateMax, 'endOfDay'),
    }),
    program: programId,
    rdiMergeStatus: IndividualRdiMergeStatus.Merged,
  };

  return (
    <TableWrapper>
      <UniversalTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllIndividualsForPopulationTableQuery}
        queriedObjectName="allIndividuals"
        initialVariables={initialVariables}
        allowSort={false}
        filterOrderBy={filter.orderBy}
        renderRow={(row) => (
          <PeopleListTableRow
            key={row.id}
            individual={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
