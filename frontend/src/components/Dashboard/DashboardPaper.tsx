import { Box, Paper } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardPaperProps {
  title: string;
  children: React.ReactNode;
}
const StyledPaper = styled(Paper)`
  padding: 20px 24px;
  margin-top: 20px;
  font-size: 18px;
  font-weight: normal;
`;
export const DashboardPaper = ({
  title,
  children,
}: DashboardPaperProps): React.ReactElement => {
  return (
    <StyledPaper>
      <Box mb={2}>{title}</Box>
      {children}
    </StyledPaper>
  );
};
