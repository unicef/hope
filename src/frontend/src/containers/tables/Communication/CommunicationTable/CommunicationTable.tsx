import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllAccountabilityCommunicationMessagesQueryVariables,
  CommunicationMessageNode,
  useAllAccountabilityCommunicationMessagesQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './CommunicationTableHeadCells';
import { CommunicationTableRow } from './CommunicationTableRow';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface CommunicationTableProps {
  filter;
  canViewDetails: boolean;
}

function CommunicationTable({
  filter,
  canViewDetails,
}: CommunicationTableProps): ReactElement {
  const { programId } = useBaseUrl();
  const { t } = useTranslation();
  const initialVariables: AllAccountabilityCommunicationMessagesQueryVariables =
    {
      createdAtRange: JSON.stringify({
        min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      }),
      program: programId,
      paymentPlan: filter.targetPopulation,
      createdBy: filter.createdBy || '',
    };
  return (
    <TableWrapper>
      <UniversalTable<
        CommunicationMessageNode,
        AllAccountabilityCommunicationMessagesQueryVariables
      >
        title={t('Messages List')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllAccountabilityCommunicationMessagesQuery}
        queriedObjectName="allAccountabilityCommunicationMessages"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <CommunicationTableRow
            key={row.id}
            message={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(CommunicationTable, 'CommunicationTable');
