import { Box, Tooltip } from '@material-ui/core';
import CheckCircleOutlineRoundedIcon from '@material-ui/icons/CheckCircleOutlineRounded';
import ErrorOutlineRoundedIcon from '@material-ui/icons/ErrorOutlineRounded';
import WarningIcon from '@material-ui/icons/Warning';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllPaymentsForTableQuery } from '../../../../__generated__/graphql';

const OrangeCircleExclamationIcon = styled(ErrorOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.orange};
`;

const RedErrorIcon = styled(ErrorOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.red};
`;

const GreenCheckIcon = styled(CheckCircleOutlineRoundedIcon)`
  color: ${({ theme }) => theme.hctPalette.green};
`;

const OrangeTriangleExclamationIcon = styled(WarningIcon)`
  color: ${({ theme }) => theme.hctPalette.orange};
`;
const RedTriangleExclamationIcon = styled(WarningIcon)`
  color: ${({ theme }) => theme.hctPalette.warningRed};
`;

interface PaymentTableWarningTooltipProps {
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  handleClick: (e: React.SyntheticEvent<HTMLDivElement>) => void;
}

export const PaymentTableWarningTooltip = ({
  payment,
  handleClick,
}: PaymentTableWarningTooltipProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    deliveredQuantity,
    entitlementQuantity,
    paymentPlanHardConflicted,
    paymentPlanSoftConflicted,
  } = payment;

  let icon = null;
  let tooltipText = '';
  const indicatingAssistanceTooltipText = t(
    'Indicating Assistance (click on the icon to see the details)',
  );

  if (deliveredQuantity === null) {
    // No icon and tooltip for null quantity
    return null;
  }
  // TODO: handle this on the backend
  const showIndicatingAssistance = true;

  if (deliveredQuantity === 0) {
    icon = <RedErrorIcon onClick={handleClick} />;
    tooltipText = t(
      'Delivered quantity is 0 (click on the icon to see the details)',
    );
  } else if (deliveredQuantity === entitlementQuantity) {
    icon = <GreenCheckIcon onClick={handleClick} />;
    tooltipText = t(
      'Delivered quantity is equal to entitlement quantity (click on the icon to see the details)',
    );
  } else if (paymentPlanSoftConflicted) {
    icon = <OrangeTriangleExclamationIcon onClick={handleClick} />;
    tooltipText = t('Soft conflict (click on the icon to see the details)');
  } else if (paymentPlanHardConflicted) {
    icon = <RedTriangleExclamationIcon onClick={handleClick} />;
    tooltipText = t('Hard conflict (click on the icon to see the details)');
  }

  return (
    <Box display='flex' alignItems='center'>
      {showIndicatingAssistance && (
        <Tooltip title={indicatingAssistanceTooltipText} arrow>
          <Box mr={1}>
            <OrangeCircleExclamationIcon onClick={handleClick} />
          </Box>
        </Tooltip>
      )}
      {icon && (
        <Tooltip title={tooltipText} arrow>
          <Box>{icon}</Box>
        </Tooltip>
      )}
    </Box>
  );
};
