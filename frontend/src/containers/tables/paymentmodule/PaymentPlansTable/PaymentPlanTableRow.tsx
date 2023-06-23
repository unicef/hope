import { Box, TableCell } from '@material-ui/core';
import React from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '../../../../utils/utils';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface PaymentPlanTableRowProps {
  plan;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentPlanPath = `/${businessArea}/payment-module/${
    plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentPlanPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  const followUpLinks = (): React.ReactElement => {
    if (!plan.followUps?.edges?.length) return <>-</>;
    return (
      <Box display='flex' flexDirection='column'>
        {plan.followUps?.edges?.map((followUp) => {
          const followUpPaymentPlanPath = `/${businessArea}/payment-module/followup-payment-plans/${followUp?.node?.id}`;
          return (
            <Box mb={1}>
              <BlackLink key={followUp?.node?.id} to={followUpPaymentPlanPath}>
                {followUp?.node?.unicefId}
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
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>
        {plan.isFollowUp ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.status}
            statusToColor={paymentPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{plan.totalHouseholdsCount || '-'}</TableCell>
      <TableCell align='left'>{plan.currencyName}</TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalEntitledQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalDeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalUndeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>{followUpLinks()}</TableCell>
    </ClickableTableRow>
  );
};
