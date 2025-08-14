import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useMemo, useState, useEffect } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { Recipient } from '@restgenerated/models/Recipient';
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
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug,
      programSlug,
      messageId: id,
    }),
    [businessAreaSlug, programSlug, id],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery({
    queryKey: [
      'businessAreasProgramsHouseholdsAllAccountabilityCommunicationMessageRecipientsList',
      queryVariables,
    ],
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
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        rowsPerPageOptions={[10, 15, 20]}
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
