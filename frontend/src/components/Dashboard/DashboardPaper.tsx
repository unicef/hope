import { Box, Paper, Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardPaperProps {
  title: string;
  children: React.ReactNode;
}
const StyledPaper = styled(Paper)`
  padding: 20px 24px;
  margin-top: 20px;
`;
export const DashboardPaper = ({
  title,
  children,
}: DashboardPaperProps): React.ReactElement => {
  return (
    <StyledPaper>
      <Box mb={2}>
        <Typography variant='h6'>{title}</Typography>
      </Box>
      {children}
    </StyledPaper>
  );
};
