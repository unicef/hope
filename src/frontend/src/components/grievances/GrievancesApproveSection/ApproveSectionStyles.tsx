import { Paper, Table } from '@mui/material';
import styled from 'styled-components';

export const ApproveBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
  overflow-x: scroll;
`;

export const StyledTable = styled(Table)`
  && {
    min-width: 100px;
  }
`;

export const BlueBold = styled.div`
  color: ${({ theme }) => theme.hctPalette.navyBlue};
  font-weight: 500;
  cursor: pointer;
`;
