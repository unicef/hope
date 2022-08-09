import { Box } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import { useTranslation } from 'react-i18next';

const WarningBox = styled(Box)`
  width: 70%;
  background-color: #fef7f7;
  color: #e90202;
`;

const ErrorOutline = styled(ErrorOutlineIcon)`
  color: #e90202;
  margin-right: 5px;
`;

export const DeliveryMechanismWarning = (): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <WarningBox mt={4} mb={4} p={3} display='flex' alignItems='center'>
      <ErrorOutline />
      {t(
        'Selected delivery mechanisms are not sufficient to serve all beneficiaries. Please add Cash and Mobile Money to move to the next step.',
      )}
    </WarningBox>
  );
};
