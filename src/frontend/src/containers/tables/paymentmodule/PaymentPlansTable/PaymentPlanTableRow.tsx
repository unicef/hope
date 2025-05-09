import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, TableCell } from '@mui/material';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface PaymentPlanTableRowProps {
  plan: PaymentPlanList;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const paymentPlanPath = `/${baseUrl}/payment-module/${
    plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    navigate(paymentPlanPath);
  };

  const followUpLinks = (): ReactElement => {
    if (!plan.followUps?.length) return <>-</>;
    return (
      <Box display="flex" flexDirection="column">
        {plan.followUps?.map((followUp) => {
          const followUpPaymentPlanPath = `/${baseUrl}/payment-module/followup-payment-plans/${followUp?.id}`;
          return (
            <Box key={followUp?.id} mb={1}>
              <BlackLink key={followUp?.id} to={followUpPaymentPlanPath}>
                {followUp?.unicefId}
              </BlackLink>
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={plan.id}
    >
      <TableCell align="left">
        {plan.isFollowUp ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={plan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">{plan.name}</TableCell>
      <TableCell align="left">{plan.totalHouseholdsCount || '-'}</TableCell>
      <TableCell align="left">{plan.currency}</TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalEntitledQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalDeliveredQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalUndeliveredQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{followUpLinks()}</TableCell>
    </ClickableTableRow>
  );
};
