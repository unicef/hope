import * as React from 'react';
import FlagIcon from '@mui/icons-material/Flag';
import { Tooltip } from '@mui/material';
import styled from 'styled-components';

interface StyledFlagProps {
  confirmed?: boolean;
}

const StyledFlag = styled(FlagIcon)<StyledFlagProps>`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;
interface FlagTooltipProps {
  confirmed?: boolean;
  message?: string;
  handleClick?: () => void;
}
export function FlagTooltip({
  confirmed,
  message = '',
  handleClick,
}: FlagTooltipProps): React.ReactElement {
  return (
    <Tooltip onClick={handleClick} title={message}>
      <StyledFlag confirmed={confirmed} />
    </Tooltip>
  );
}
