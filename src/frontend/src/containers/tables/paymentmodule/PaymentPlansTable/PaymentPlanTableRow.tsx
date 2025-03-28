import { Box, TableCell } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface PaymentPlanTableRowProps {
  plan: Partial<PaymentPlanDetail>;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const paymentPlanPath = `/${baseUrl}/payment-module/${
    plan.is_follow_up ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    navigate(paymentPlanPath);
  };
  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  const followUpLinks = (): ReactElement => {
    if (!plan.follow_ups?.length) return <>-</>;
    return (
      <Box display="flex" flexDirection="column">
        {plan.follow_ups?.map((followUp) => {
          const followUpPaymentPlanPath = `/${baseUrl}/payment-module/followup-payment-plans/${followUp?.id}`;
          return (
            <Box key={followUp?.id} mb={1}>
              <BlackLink key={followUp?.id} to={followUpPaymentPlanPath}>
                {followUp?.unicef_id}
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
        {plan.is_follow_up ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicef_id}</BlackLink>
        ) : (
          plan.unicef_id
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={plan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">{plan.name}</TableCell>
      <TableCell align="left">{plan.total_households_count || '-'}</TableCell>
      <TableCell align="left">{plan.currency}</TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.total_entitled_quantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.total_delivered_quantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.total_undelivered_quantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersion_start_date}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersion_end_date}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{followUpLinks()}</TableCell>
    </ClickableTableRow>
  );
};
