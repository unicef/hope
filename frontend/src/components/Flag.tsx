import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import FlagIcon from '@material-ui/icons/Flag';
import styled from 'styled-components';
import { MiśTheme } from '../theme';

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
