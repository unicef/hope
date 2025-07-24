import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '@components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Paper, Typography } from '@mui/material';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { PaymentList } from '@restgenerated/models/PaymentList';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
  canViewDetails?: boolean;
}

function PaymentsTable({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
}: PaymentsTableProps): ReactElement {
  const { baseUrl, programId } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const [dialogPayment, setDialogPayment] = useState<PaymentList | null>(null);
  const initialQueryVariables = {
    businessAreaSlug: businessArea,
    programSlug: programId,
    paymentPlanId: paymentPlan.id,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      queryVariables,
      businessArea,
      programId,
      paymentPlan.id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansPaymentsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentPlanId: paymentPlan.id,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const replacements = {
    household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ${t('ID')}`,
    household__size: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ${t('Size')}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <>
      <TableWrapper>
        <Paper>
          <StyledBox p={6} display="flex" justifyContent="space-between">
            <Typography data-cy="table-title" variant="h6">
              {t('Payee List')}
            </Typography>
            {(paymentPlan.status === PaymentPlanStatusEnum.ACCEPTED ||
              paymentPlan.status === PaymentPlanStatusEnum.FINISHED) && (
              <ImportXlsxPaymentPlanPaymentListPerFsp
                paymentPlan={paymentPlan}
                permissions={permissions}
              />
            )}
          </StyledBox>
          <UniversalRestTable
            isOnPaper={false}
            headCells={adjustedHeadCells}
            rowsPerPageOptions={[10, 25, 50]}
            defaultOrderBy="createdAt"
            defaultOrderDirection="desc"
            isLoading={isLoading}
            error={error}
            queryVariables={queryVariables}
            setQueryVariables={setQueryVariables}
            data={paymentsData}
            renderRow={(row: PaymentList) => (
              <PaymentsTableRow
                key={row.id}
                payment={row}
                canViewDetails={canViewDetails}
                onWarningClick={(payment) => {
                  setDialogPayment(payment);
                }}
                permissions={permissions}
              />
            )}
          />
        </Paper>
      </TableWrapper>
      <WarningTooltipTable
        paymentPlan={paymentPlan}
        payment={dialogPayment}
        setDialogOpen={() => setDialogPayment(null)}
        canViewDetails={canViewDetails}
        baseUrl={baseUrl}
      />
    </>
  );
}

export default withErrorBoundary(PaymentsTable, 'PaymentsTable');
