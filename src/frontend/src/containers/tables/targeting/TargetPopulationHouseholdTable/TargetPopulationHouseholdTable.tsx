import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { headCells } from './TargetPopulationHouseholdHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationHouseholdRow';

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
  const { businessArea, programId } = useBaseUrl();
  const initialQueryVariables = {
    ...(id && { paymentPlanId: id }),
    ...variables,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  //TODO: pass household id to payments query
  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      businessArea,
      programId,
      queryVariables,
      paymentPlan.id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansPaymentsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        paymentPlanId: paymentPlan.id,
      });
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
        data={paymentsData}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        renderRow={(row: PaymentList) => (
          <TargetPopulationHouseholdTableRow
            key={(row as { id: string }).id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
