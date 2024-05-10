import styled from 'styled-components';
import { Paper } from '@mui/material';

export const Overview = styled(Paper)`
  margin: 20px;
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
`;
