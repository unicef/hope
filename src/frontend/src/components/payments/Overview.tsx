import styled from 'styled-components';
import { Paper, Theme } from '@mui/material';

export const Overview = styled(Paper)<{ theme?: Theme }>`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;
