import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { Recipient } from '@restgenerated/models/Recipient';
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
  const { businessAreaSlug, programCode } = useBaseUrl();

  const table = useTableState({ rowsPerPageOptions: [10, 15, 20] });
  const queryVariables = useMemo(
    () => ({
      businessAreaSlug,
      programCode,
      messageId: id,
      ...table.paginationParams,
    }),
    [businessAreaSlug, programCode, id, table.paginationParams],
  );

  const { data, isLoading, error } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsHouseholdsAllAccountabilityCommunicationMessageRecipientsList,
      queryVariables,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsAllAccountabilityCommunicationMessageRecipientsList(
        queryVariables,
      ),
  });

  const replacements = {
    unicefId: (bg) => `${bg?.groupLabel} ID`,
    head_of_household__full_name: (bg) => `Head of ${bg?.groupLabel}`,
    size: (bg) => `${bg?.groupLabel} Size`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('Recipients')}
        headCells={adjustedHeadCells}
        data={data}
        error={error}
        isLoading={isLoading}
        tableState={table}
        itemsCount={data?.results?.length || 0}
        renderRow={(row: Recipient) => (
          <RecipientsTableRow
            key={row.id}
            household={row}
            headOfHousehold={row.headOfHousehold}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(RecipientsTable, 'RecipientsTable');
