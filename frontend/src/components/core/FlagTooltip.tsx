import React from 'react';
import FlagIcon from '@mui/icons-material/Flag';
import { Tooltip } from '@mui/material';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.orange};
`;
interface FlagTooltipProps {
  confirmed?: boolean;
  message?: string;
  handleClick?: () => void;
}
export const FlagTooltip = ({
  confirmed,
  message = '',
  handleClick,
}: FlagTooltipProps): React.ReactElement => {
  return (
    <Tooltip onClick={handleClick} title={message}>
      <StyledFlag confirmed={confirmed ? 1 : 0} />
    </Tooltip>
  );
};
