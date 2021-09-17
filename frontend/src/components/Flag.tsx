import React from 'react';
import FlagIcon from '@material-ui/icons/Flag';
import { Tooltip } from '@material-ui/core';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.oragne};
`;
interface FlagProps {
  confirmed?: boolean;
  message?: string;
}
export const Flag = ({
  confirmed,
  message = '',
}: FlagProps): React.ReactElement => {
  return (
    <Tooltip title={message}>
      <StyledFlag confirmed={confirmed} />
    </Tooltip>
  );
};
