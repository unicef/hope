import React from 'react';
import FlagIcon from '@material-ui/icons/Flag';
import styled from 'styled-components';

const StyledFlag = styled(FlagIcon)`
  color: ${({ theme, confirmed }) =>
    confirmed ? 'deeppink' : theme.hctPalette.oragne};
`;
interface FlagProps {
  confirmed?: boolean;
}
export const Flag = ({ confirmed }: FlagProps): React.ReactElement => {
  return <StyledFlag confirmed={confirmed} />;
};
