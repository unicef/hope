import React from 'react';
import styled from 'styled-components';
import { Tooltip } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';

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
