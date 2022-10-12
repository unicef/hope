import React from 'react';
import FlagIcon from '@material-ui/icons/Flag';
import { Tooltip } from '@material-ui/core';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.oragne};
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
      <StyledFlag confirmed={confirmed} />
    </Tooltip>
  );
};
