import { Paper } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardCardPageProps {
  color: string;
}
const StyledPaper = styled(Paper)`
  border-left: 3px solid ${({ color }) => color};
`;
export const DashboardCard = ({
  color,
}: DashboardCardPageProps): React.ReactElement => {
  return <StyledPaper color={color}>Card</StyledPaper>;
};
