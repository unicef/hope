import React from 'react';
import styled from 'styled-components';
import { Tooltip } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';

const StyledWarning = styled(WarningIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;

interface WarningTooltipProps {
  confirmed?: boolean;
  message?: string;
}
export const WarningTooltip = ({
  confirmed = false,
  message = '',
}: WarningTooltipProps): React.ReactElement => {
  return (
    <Tooltip title={message}>
      <StyledWarning confirmed={confirmed ? 1 : 0} />
    </Tooltip>
  );
};
