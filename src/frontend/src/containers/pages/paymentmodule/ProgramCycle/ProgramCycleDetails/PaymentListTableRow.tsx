import type { ReactElement } from 'react';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { StatusBox } from '@core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentListStatusToColor,
} from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { LinkedPaymentListsModal } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/LinkedPaymentListsModal';
import type { PaymentListList } from '@restgenerated/models/PaymentListList';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';

interface PaymentListTableRowProps {
  paymentList: PaymentListList;
  canViewDetails: boolean;
}

export const PaymentListTableRow = ({
  paymentList,
  canViewDetails,
}: PaymentListTableRowProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  // A payment plan lists its target populations too; those still live in Targeting.
  const isTargetPopulation =
    paymentList.status === PaymentListStatusEnum.DRAFT ||
    !!paymentList.status?.startsWith('TP_');
  const paymentListPath = isTargetPopulation
    ? `/${baseUrl}/target-population/${paymentList.id}`
    : `/${baseUrl}/payment-module/${
        paymentList.planType === 'FOLLOW_UP'
          ? 'followup-payment-lists'
          : 'payment-lists'
      }/${paymentList.id}`;

  return (
    <ClickableTableRow key={paymentList.id}>
      <TableCell align="left">
        {paymentList.planType === 'FOLLOW_UP' ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentListPath}>{paymentList.unicefId}</BlackLink>
        ) : (
          paymentList.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentList.status}
          statusToColor={paymentListStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {paymentList.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentList.totalEntitledQuantity), paymentList.currency, paymentList.currencyVisionCode)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentList.totalUndeliveredQuantity), paymentList.currency, paymentList.currencyVisionCode)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentList.totalDeliveredQuantity), paymentList.currency, paymentList.currencyVisionCode)}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentList.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentList.dispersionEndDate}</UniversalMoment>
      </TableCell>

      <TableCell align="left">
        <LinkedPaymentListsModal
          paymentList={paymentList}
          canViewDetails={canViewDetails}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
