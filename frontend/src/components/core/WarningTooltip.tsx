import * as React from 'react';
import styled from 'styled-components';
import { Tooltip, TooltipProps } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';

interface StyledWarningProps {
  confirmed: boolean;
}

const StyledWarning = styled(WarningIcon)<StyledWarningProps>`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;

interface WarningTooltipProps {
  confirmed?: boolean;
  message?: string;
  handleClick?: TooltipProps['onClick'];
}

export function WarningTooltip({
  confirmed = false,
  message = '',
  handleClick,
}: WarningTooltipProps): React.ReactElement {
  return (
    <Tooltip onClick={handleClick} title={message}>
      <StyledWarning confirmed={confirmed} />
    </Tooltip>
  );
}
