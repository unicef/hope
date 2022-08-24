import { Box } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';

const WarningBox = styled(Box)`
  width: 70%;
  background-color: #fef7f7;
  color: #e90202;
`;

const ErrorOutline = styled(ErrorOutlineIcon)`
  color: #e90202;
  margin-right: 5px;
`;

interface DeliveryMechanismWarningProps {
  warning: string;
}

export const DeliveryMechanismWarning = ({
  warning,
}: DeliveryMechanismWarningProps): React.ReactElement => {
  return (
    <WarningBox mt={4} mb={4} p={3} display='flex' alignItems='center'>
      <ErrorOutline />
      {warning}
    </WarningBox>
  );
};
