import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded';
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';
import { BlackLink } from '@components/core/BlackLink';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { WarningTooltip } from '@components/core/WarningTooltip';
import {
  formatCurrencyWithSymbol,
  opacityToHex,
  renderSomethingOrDash,
} from '@utils/utils';
import { AllPaymentsForTableQuery, PaymentStatus } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

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
  padding: ${({ theme }) => theme.spacing(1)};
  text-align: center;
  margin-right: 20px;
`;

const OrangeError = styled(ErrorOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.orange};
`;

const RedError = styled(ErrorOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.red};
`;

const GreenCheck = styled(CheckCircleOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.green};
`;

interface PaymentsTableRowProps {
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  canViewDetails: boolean;
  onWarningClick?: (
    payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'],
  ) => void;
  permissions;
}

export function PaymentsTableRow({
  payment,
  canViewDetails,
  onWarningClick,
  permissions,
}: PaymentsTableRowProps): React.ReactElement {
  const { t } = useTranslation();
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
    const { deliveredQuantity, currency, deliveredQuantityUsd, status } =
      payment;
    if (status === PaymentStatus.TransactionErroneous) {
      return <RoutedBox>UNSUCCESSFUL</RoutedBox>;
    }
    if (status === PaymentStatus.ManuallyCancelled) {
      return <RoutedBox>CANCELLED</RoutedBox>;
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

  const renderMark = (): React.ReactElement => {
    const { deliveredQuantity, entitlementQuantity } = payment;

    if (deliveredQuantity === null) {
      return <></>;
    }
    if (deliveredQuantity === 0) {
      return <RedError />;
    }
    if (deliveredQuantity === entitlementQuantity) {
      return <GreenCheck />;
    }
    return <OrangeError />;
  };

  return (
    <ClickableTableRow hover role="checkbox" key={payment.id}>
      <TableCell align="left">
        {(payment.paymentPlanHardConflicted ||
          payment.paymentPlanSoftConflicted) && (
          <WarningTooltip
            handleClick={(e) => handleDialogWarningOpen(e)}
            message={t(
              'This household is also included in other Payment Plans. Click this icon to view details.',
            )}
            confirmed={payment.paymentPlanHardConflicted}
          />
        )}
      </TableCell>
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={paymentDetailsPath}>{payment.unicefId}</BlackLink>
        ) : (
          payment.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={householdDetailsPath}>
            {payment.household.unicefId}
          </BlackLink>
        ) : (
          payment.household.unicefId
        )}
      </TableCell>
      <TableCell align="left">{payment.household.size}</TableCell>
      <TableCell align="left">
        {renderSomethingOrDash(payment.household.admin2?.name)}
      </TableCell>
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={collectorDetailsPath}>
            {payment.collector.fullName}
          </BlackLink>
        ) : (
          payment.collector.fullName
        )}
      </TableCell>
      <TableCell align="left">
        {payment.financialServiceProvider
          ? payment.financialServiceProvider.name
          : '-'}
      </TableCell>
      <TableCell align="left">
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
      <TableCell data-cy="delivered-quantity-cell" align="left">
        {renderDeliveredQuantity()}
      </TableCell>
      {hasPermissions(PERMISSIONS.PM_VIEW_FSP_AUTH_CODE, permissions) && (
        <TableCell data-cy="fsp-auth-code-cell" align="left">
          {payment.fspAuthCode || '-'}
        </TableCell>
      )}
      <TableCell>{renderMark()}</TableCell>
    </ClickableTableRow>
  );
}
