import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createApiParams } from '@utils/apiUtils';
import { useProgramContext } from 'src/programContext';
import { headCells } from './TargetPopulationHouseholdHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationHouseholdRow';
import { PendingPayment } from '@restgenerated/models/PendingPayment';
import { PaginatedPendingPaymentList } from '@restgenerated/models/PaginatedPendingPaymentList';

interface TargetPopulationHouseholdProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationHouseholdTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationHouseholdProps): ReactElement {
  const { t } = useTranslation();
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const [page, setPage] = useState(0);

  const initialQueryVariables = useMemo(
    () => ({
      ...variables,
      businessAreaSlug,
      programSlug,
      id,
    }),
    [variables, businessAreaSlug, programSlug, id],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: householdsData,
    isLoading,
    error,
  } = useQuery<PaginatedPendingPaymentList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      businessAreaSlug,
      programSlug,
      queryVariables,
      id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsList(
        createApiParams(
          {
            businessAreaSlug,
            programSlug,
            id,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  // Add count query for pending payments
  const { data: countData } = useQuery({
    queryKey: [
      'businessAreasProgramsTargetPopulationsPendingPaymentsCount',
      businessAreaSlug,
      programSlug,
      id,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsCountRetrieve(
        {
          businessAreaSlug,
          programSlug,
          id,
        },
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    household_unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    household_size: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t(`${beneficiaryGroup?.groupLabelPlural}`)}
        headCells={adjustedHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        isLoading={isLoading}
        data={householdsData}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={itemsCount}
        page={page}
        setPage={setPage}
        renderRow={(row: PendingPayment) => (
          <TargetPopulationHouseholdTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
