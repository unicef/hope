import { Paper } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardCardProps {
  color: string;
  children: React.ReactNode;
}
const StyledPaper = styled(Paper)`
  border-left: 4px solid ${({ color }) => color};
  padding: 20px 24px;
`;
export const DashboardCard = ({
  color,
  children,
}: DashboardCardProps): React.ReactElement => {
  return <StyledPaper color={color}>{children}</StyledPaper>;
};
