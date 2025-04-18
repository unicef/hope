import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { WarningTooltip } from '@components/core/WarningTooltip';
import { useBaseUrl } from '@hooks/useBaseUrl';
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded';
import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';
import TableCell from '@mui/material/TableCell';
import { PaymentList } from '@restgenerated/models/PaymentList';
import {
  formatCurrencyWithSymbol,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  renderSomethingOrDash,
} from '@utils/utils';
import { ReactElement, SyntheticEvent } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

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
  payment: PaymentList;
  canViewDetails: boolean;
  onWarningClick?: (payment: PaymentList) => void;
  permissions;
}

export function PaymentsTableRow({
  payment,
  canViewDetails,
  onWarningClick,
  permissions,
}: PaymentsTableRowProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const paymentDetailsPath = `/${baseUrl}/payment-module/payments/${payment.id}`;
  const householdDetailsPath = `/${baseUrl}/population/household/${payment.householdId}`;
  const collectorDetailsPath = `/${baseUrl}/population/individuals/${payment.collectorId}`;

  const handleDialogWarningOpen = (e: SyntheticEvent<HTMLDivElement>): void => {
    e.stopPropagation();
    onWarningClick(payment);
  };

  const renderDeliveredQuantity = (): ReactElement => {
    const { deliveredQuantity, currency, deliveredQuantityUsd } = payment;

    if (deliveredQuantity === null) {
      return <>-</>;
    }
    return (
      <>
        {`${formatCurrencyWithSymbol(deliveredQuantity, currency)}
        (${formatCurrencyWithSymbol(deliveredQuantityUsd, 'USD')})`}
      </>
    );
  };

  const renderMark = (): ReactElement => {
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
      <TableCell>
        <StatusBox
          status={payment.status}
          statusToColor={paymentStatusToColor}
          statusNameMapping={paymentStatusDisplayMap}
        />
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
