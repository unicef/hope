import React from 'react';
import styled from 'styled-components';
import { Tooltip } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';

const StyledWarning = styled(WarningIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.oragne};
`;

interface WarningTooltipProps {
  confirmed?: boolean;
  message?: string;
}
export const WarningTooltip = ({
  confirmed,
  message = '',
}: WarningTooltipProps): React.ReactElement => {
  return (
    <Tooltip title={message}>
      <StyledWarning confirmed={confirmed} />
    </Tooltip>
  );
};
