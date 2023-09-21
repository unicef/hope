import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import styled from 'styled-components';
import {
  AllPaymentsForTableQuery,
  PaymentStatus,
} from '../../../../__generated__/graphql';
import { BlackLink } from '../../../../components/core/BlackLink';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import {
  formatCurrencyWithSymbol,
  opacityToHex,
  renderSomethingOrDash,
} from '../../../../utils/utils';
import { PaymentTableWarningTooltip } from './PaymentTableWarningTooltip';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

const RoutedBox = styled.div`
  color: ${({ theme }) => theme.hctPalette.red};
  background-color: ${({ theme }) =>
    `${theme.hctPalette.red}${opacityToHex(0.15)}`};
  border-radius: 16px;
  font-family: Roboto;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  line-height: 16px;
  padding: ${({ theme }) => theme.spacing(1)}px;
  text-align: center;
  margin-right: 20px;
`;

interface PaymentsTableRowProps {
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  canViewDetails: boolean;
  onWarningClick?: (
    payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'],
  ) => void;
}

export const PaymentsTableRow = ({
  payment,
  canViewDetails,
  onWarningClick,
}: PaymentsTableRowProps): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const paymentDetailsPath = `/${baseUrl}/payment-module/payments/${payment.id}`;
  const householdDetailsPath = `/${baseUrl}/population/household/${payment.household.id}`;
  const collectorDetailsPath = `/${baseUrl}/population/individuals/${payment.collector.id}`;

  const handleDialogWarningOpen = (
    e: React.SyntheticEvent<HTMLDivElement>,
  ): void => {
    e.stopPropagation();
    onWarningClick(payment);
  };

  const renderDeliveredQuantity = (): React.ReactElement => {
    const {
      deliveredQuantity,
      currency,
      deliveredQuantityUsd,
      status,
    } = payment;
    if (status === PaymentStatus.TransactionErroneous) {
      return <RoutedBox>UNSUCCESSFUL</RoutedBox>;
    }
    if (deliveredQuantity === null) {
      return <></>;
    }
    return (
      <>
        {`${formatCurrencyWithSymbol(deliveredQuantity, currency)}
        (${formatCurrencyWithSymbol(deliveredQuantityUsd, 'USD')})`}
      </>
    );
  };

  return (
    <ClickableTableRow hover role='checkbox' key={payment.id}>
      <TableCell align='left'>
        <PaymentTableWarningTooltip
          payment={payment}
          handleClick={handleDialogWarningOpen}
        />
      </TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={paymentDetailsPath}>{payment.unicefId}</BlackLink>
        ) : (
          payment.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>
            {payment.household.unicefId}
          </BlackLink>
        ) : (
          payment.household.unicefId
        )}
      </TableCell>
      <TableCell align='left'>{payment.household.size}</TableCell>
      <TableCell align='left'>
        {renderSomethingOrDash(payment.household.admin2?.name)}
      </TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={collectorDetailsPath}>
            {payment.collector.fullName}
          </BlackLink>
        ) : (
          payment.collector.fullName
        )}
      </TableCell>
      <TableCell align='left'>
        {payment.financialServiceProvider
          ? payment.financialServiceProvider.name
          : '-'}
      </TableCell>
      <TableCell align='left'>
        {payment.entitlementQuantity != null && payment.entitlementQuantity >= 0
          ? `${formatCurrencyWithSymbol(
              payment.entitlementQuantity,
              payment.currency,
            )} (${formatCurrencyWithSymbol(
              payment.entitlementQuantityUsd,
              'USD',
            )})`
          : '-'}
      </TableCell>
      <TableCell data-cy='delivered-quantity-cell' align='left'>
        {renderDeliveredQuantity()}
      </TableCell>
    </ClickableTableRow>
  );
};
