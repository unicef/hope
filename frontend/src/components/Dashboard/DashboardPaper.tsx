import { Box, Paper } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardPaperProps {
  title?: string;
  children: React.ReactNode;
  noMarginTop?: boolean;
  extraPaddingLeft?: boolean;
}
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const StyledPaper = styled(({ noMarginTop, extraPaddingLeft, ...props }) => (
  <Paper {...props} />
))`
  padding: 20px 24px;
  padding-left: ${(props) => (props.extraPaddingLeft ? '46px' : '24px')}
  margin-top: ${(props) => (props.noMarginTop ? '0' : '20px')};
  font-size: 18px;
  font-weight: normal;
`;
export const DashboardPaper = ({
  title,
  children,
  noMarginTop,
  extraPaddingLeft,
}: DashboardPaperProps): React.ReactElement => {
  return (
    <StyledPaper noMarginTop={noMarginTop} extraPaddingLeft={extraPaddingLeft}>
      {title && <Box mb={2}>{title}</Box>}
      {children}
    </StyledPaper>
  );
};
