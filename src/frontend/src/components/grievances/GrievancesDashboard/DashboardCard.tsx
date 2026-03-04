import { Paper } from '@mui/material';
import { ReactNode, ReactElement } from 'react';
import styled from 'styled-components';

interface DashboardCardProps {
  color: string;
  children: ReactNode;
}
export const CardTitle = styled.div`
  color: #6f6f6f;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 1.75px;
  padding-bottom: 5px;
`;

export const CardAmountSmaller = styled.div`
  color: rgba(0, 0, 0, 0.87);
  font-weight: 600;
  font-size: 20px;
`;

interface StyledPaperProps {
  color: string;
}

const StyledPaper = styled(Paper)<StyledPaperProps>`
  border-left: 4px solid ${({ color }) => color};
  padding: 20px 24px;
`;
export function DashboardCard({
  color,
  children,
}: DashboardCardProps): ReactElement {
  return <StyledPaper color={color}>{children}</StyledPaper>;
}
