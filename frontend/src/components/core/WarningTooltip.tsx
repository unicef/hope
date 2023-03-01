import React from 'react';
import styled from 'styled-components';
import { Tooltip, TooltipProps } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';

const StyledWarning = styled(WarningIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;

interface WarningTooltipProps {
  confirmed?: boolean;
  message?: string;
  handleClick?: TooltipProps['onClick'];
}

export const WarningTooltip = ({
  confirmed = false,
  message = '',
  handleClick,
}: WarningTooltipProps): React.ReactElement => {
  return (
    <Tooltip onClick={handleClick} title={message}>
      <StyledWarning confirmed={confirmed ? 1 : 0} />
    </Tooltip>
  );
};
