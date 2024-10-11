import { Paper } from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';

interface DashboardCardProps {
  color: string;
  children: React.ReactNode;
}
export const CardTitle = styled.div`
  color: #6f6f6f;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 1.75px;
  padding-bottom: 5px;
`;
export const CardTextLight = styled.div`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 1.75px;
`;
export const CardTextLightLarge = styled.div`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: 16px;
`;
export const CardAmount = styled.div`
  text-transform: capitalize;
  color: rgba(0, 0, 0, 0.87);
  font-weight: 600;
  font-size: 24px;
`;

interface IconContainerProps {
  bg: string;
  color: string;
}
export const IconContainer = styled.div<IconContainerProps>`
  height: 40px;
  width: 40px;
  padding: 8px;
  border-radius: 3px;
  background-color: ${({ bg }) => bg};
  color: ${({ color }) => color};
  font-size: 24px;
`;
export const CardAmountSmaller = styled.div`
  color: rgba(0, 0, 0, 0.87);
  font-weight: 600;
  font-size: 20px;
`;
export const CardAmountLink = styled.div`
  text-transform: capitalize;
  text-decoration: underline;
  cursor: pointer;
  color: #033f91;
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
}: DashboardCardProps): React.ReactElement {
  return <StyledPaper color={color}>{children}</StyledPaper>;
}
