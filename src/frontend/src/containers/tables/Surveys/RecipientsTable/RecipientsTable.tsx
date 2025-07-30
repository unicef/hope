import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';
import { ReactElement, useMemo, useState, useEffect } from 'react';
import { adjustHeadCells } from '@utils/utils';
import { Recipient } from '@restgenerated/models/Recipient';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useQuery } from '@tanstack/react-query';

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
      surveyId: id,
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
      <UniversalRestTable<Recipient, typeof initialQueryVariables>
        title={t('Recipients')}
        headCells={adjustedHeadCells}
        data={data}
        error={error}
        isLoading={isLoading}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        rowsPerPageOptions={[10, 15, 20]}
        itemsCount={data.results?.length || 0}
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
