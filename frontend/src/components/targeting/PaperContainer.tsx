import styled from 'styled-components';
import { Paper } from '@mui/material';

export const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(4)};
  margin: ${({ theme }) => theme.spacing(5)};
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;
