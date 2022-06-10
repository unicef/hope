import React from 'react';
import FlagIcon from '@mui/icons-material/Flag';
import { Tooltip } from '@mui/material';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.oragne};
`;
interface FlagTooltipProps {
  confirmed?: boolean;
  message?: string;
}
export const FlagTooltip = ({
  confirmed,
  message = '',
}: FlagTooltipProps): React.ReactElement => {
  return (
    <Tooltip title={message}>
      <StyledFlag confirmed={confirmed} />
    </Tooltip>
  );
};
