import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';
import { RestService } from '@restgenerated/services/RestService';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';
import { ReactElement, useMemo } from 'react';
import { adjustHeadCells } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
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
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const initialVariables = useMemo(
    () => ({
      survey: id,
    }),
    [id],
  );

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
      <UniversalRestQueryTable
        title={t('Recipients')}
        headCells={adjustedHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={
          RestService.restBusinessAreasProgramsHouseholdsAllAccountabilityCommunicationMessageRecipientsList
        }
        queryVariables={{ businessAreaSlug, programSlug, ...initialVariables }}
        setQueryVariables={() => {}}
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
