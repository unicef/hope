import { Box, Paper } from '@mui/material';
import { ReactNode, ReactElement } from 'react';
import styled from 'styled-components';

interface DashboardPaperProps {
  title?: string;
  children: ReactNode;
  noMarginTop?: boolean;
  extraPaddingLeft?: boolean;
  extraPaddingTitle?: boolean;
  color?: string;
}
const StyledPaper = styled(({ ...props }) => <Paper {...props} />)`
  padding: 18px 24px;
  padding-left: ${(props) => (props.extraPaddingLeft ? '46px' : '24px')}
  margin-top: ${(props) => (props.noMarginTop ? '0' : '20px')};
  font-size: 18px;
  font-weight: normal;
  && > p {
    color: ${(props) => props.color || 'inherit'}
  }
`;
export function DashboardPaper({
  title,
  children,
  noMarginTop,
  extraPaddingLeft,
  extraPaddingTitle = true,
  color,
}: DashboardPaperProps): ReactElement {
  return (
    <StyledPaper
      noMarginTop={noMarginTop}
      extraPaddingLeft={extraPaddingLeft}
      color={color}
    >
      {title && <Box mb={extraPaddingTitle ? 6 : 2}>{title}</Box>}
      {children}
    </StyledPaper>
  );
}
