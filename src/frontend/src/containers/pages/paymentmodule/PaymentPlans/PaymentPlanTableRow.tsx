import type { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { paymentListStatusToColor } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

interface PaymentPlanTableRowProps {
  paymentPlan: PaymentPlanList;
}

export const PaymentPlanTableRow = ({
  paymentPlan,
}: PaymentPlanTableRowProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();
  const paymentPlanPath = `/${baseUrl}/payment-module/payment-plans/${paymentPlan.id}`;

  return (
    <ClickableTableRow
      key={paymentPlan.id}
      onClick={() => navigate(paymentPlanPath)}
    >
      <TableCell align="left">{paymentPlan.cycle?.title || '-'}</TableCell>
      <TableCell align="left" data-cy="payment-plan-name">
        <BlackLink to={paymentPlanPath}>{paymentPlan.name}</BlackLink>
      </TableCell>
      <TableCell align="left">{paymentPlan.unicefId || '-'}</TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentPlan.status}
          statusToColor={paymentListStatusToColor}
          dataCy="payment-plan-status"
        />
      </TableCell>
    </ClickableTableRow>
  );
};
