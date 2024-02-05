import { Box } from '@mui/material';
import React from 'react';
import styled from 'styled-components';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

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
    <WarningBox
      data-cy="warning-box"
      mt={4}
      mb={4}
      p={3}
      display="flex"
      alignItems="center"
    >
      <ErrorOutline />
      {warning}
    </WarningBox>
  );
};
