import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './TargetPopulationPeopleHeadCells';
import { TargetPopulationPeopleTableRow } from './TargetPopulationPeopleRow';
import { useAllPaymentsForTableQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentList } from '@restgenerated/models/PaymentList';

interface TargetPopulationPeopleTableProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const initialQueryVariables = {
    businessArea,
    ...(id && { paymentPlanId: id }),
    ...variables,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  //TODO: add hh (people id)
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

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={paymentsData}
        renderRow={(row: PaymentList) => (
          <TargetPopulationPeopleTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
