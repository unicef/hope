import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
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

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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
      <UniversalRestTable
        title={t(`${beneficiaryGroup?.groupLabelPlural}`)}
        headCells={adjustedHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        isLoading={isLoading}
        data={householdsData}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
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
