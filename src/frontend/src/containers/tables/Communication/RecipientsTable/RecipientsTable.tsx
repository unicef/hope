import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import {
  AllAccountabilityCommunicationMessageRecipientsQueryVariables,
  CommunicationMessageRecipientMapNode,
  useAllAccountabilityCommunicationMessageRecipientsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface RecipientsTableProps {
  id: string;
  canViewDetails: boolean;
}

function RecipientsTable({
  id,
  canViewDetails,
}: RecipientsTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialVariables: AllAccountabilityCommunicationMessageRecipientsQueryVariables =
    {
      messageId: id,
    };

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <TableWrapper>
      <UniversalTable<
        CommunicationMessageRecipientMapNode,
        AllAccountabilityCommunicationMessageRecipientsQueryVariables
      >
        title={t('Recipients')}
        headCells={adjustedHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllAccountabilityCommunicationMessageRecipientsQuery}
        queriedObjectName="allAccountabilityCommunicationMessageRecipients"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <RecipientsTableRow
            key={row.id}
            household={row.headOfHousehold.household}
            headOfHousehold={row.headOfHousehold}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(RecipientsTable, 'RecipientsTable');
