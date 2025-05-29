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
  opacityToHex,
  paymentStatusDisplayMap,
  paymentStatusToColor,
  renderSomethingOrDash,
} from '@utils/utils';
import { ReactElement, SyntheticEvent } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { PaymentStatus } from '@generated/graphql';

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

interface PeoplePaymentsTableRowProps {
  payment: PaymentList;
  canViewDetails: boolean;
  onWarningClick?: (payment: PaymentList) => void;
  permissions;
}

export const PeoplePaymentsTableRow = ({
  payment,
  canViewDetails,
  onWarningClick,
  permissions,
}: PeoplePaymentsTableRowProps): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const paymentDetailsPath = `/${baseUrl}/payment-module/payments/${payment.id}`;

  const handleDialogWarningOpen = (e: SyntheticEvent<HTMLDivElement>): void => {
    e.stopPropagation();
    onWarningClick(payment);
  };

  const renderDeliveredQuantity = (): ReactElement => {
    const { deliveredQuantity, currency, deliveredQuantityUsd, status } =
      payment;
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

  const renderMark = (): ReactElement => {
    const { deliveredQuantity, entitlementQuantity } = payment;

    if (deliveredQuantity === null) {
      return <></>;
    }
    if (Number(deliveredQuantity) === 0) {
      return <RedError />;
    }
    if (deliveredQuantity === entitlementQuantity) {
      return <GreenCheck />;
    }
    return <OrangeError />;
  };

  const individual = payment?.peopleIndividual;
  const individualDetailsPath = `/${baseUrl}/population/people/${individual?.id}`;

  return (
    <ClickableTableRow hover role="checkbox" key={payment.id}>
      <TableCell align="left">
        {(payment.paymentPlanHardConflicted ||
          payment.paymentPlanSoftConflicted) && (
          <WarningTooltip
            handleClick={(e) => handleDialogWarningOpen(e)}
            message={t(
              'This individual is also included in other Payment Plans. Click this icon to view details.',
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
          <BlackLink to={individualDetailsPath}>
            {individual?.unicefId}
          </BlackLink>
        ) : (
          individual?.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={individualDetailsPath}>
            {individual?.fullName}
          </BlackLink>
        ) : (
          individual?.fullName
        )}
      </TableCell>
      <TableCell align="left">
        {renderSomethingOrDash(payment.householdAdmin2)}
      </TableCell>

      <TableCell align="left">
        {payment.fspName ? payment.fspName : '-'}
      </TableCell>
      <TableCell align="left">
        {payment.entitlementQuantity != null &&
        Number(payment.entitlementQuantity) >= 0
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
};
