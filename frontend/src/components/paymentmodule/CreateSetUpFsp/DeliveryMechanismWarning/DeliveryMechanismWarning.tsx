import { Box } from '@material-ui/core';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import React from 'react';
import styled from 'styled-components';

const StyledBox = styled(Box)`
  background-color: #fef7f7;
  width: 100%;
`;

const StyledText = styled(Box)`
  color: #e90202;
`;
const ErrorOutline = styled(ErrorOutlineIcon)`
  color: #e90202;
  margin-right: 5px;
`;

interface DeliveryMechanismWarningProps {
  text: string;
}

export const DeliveryMechanismWarning = ({
  text,
}: DeliveryMechanismWarningProps): React.ReactElement => {
  return (
    <StyledBox display='flex' alignItems='center' p={6}>
      <StyledText display='flex' alignItems='center'>
        <ErrorOutline />
        {text}
      </StyledText>
    </StyledBox>
  );
};
