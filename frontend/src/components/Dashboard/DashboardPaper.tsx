import {Box, Paper} from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';

interface DashboardPaperProps {
  title?: string;
  children: React.ReactNode;
  noMarginTop?: boolean;
  extraPaddingLeft?: boolean;
  extraPaddingTitle?: boolean;
  color?: string;
}
const StyledPaper = styled(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ({ noMarginTop, extraPaddingLeft, color, ...props }) => <Paper {...props} />,
)`
  padding: 18px 24px;
  padding-left: ${(props) => (props.extraPaddingLeft ? '46px' : '24px')}
  margin-top: ${(props) => (props.noMarginTop ? '0' : '20px')};
  font-size: 18px;
  font-weight: normal;
  && > p {
    color: ${(props) => props.color || 'inherit'}
  }
`;
export const DashboardPaper = ({
  title,
  children,
  noMarginTop,
  extraPaddingLeft,
  extraPaddingTitle = true,
  color,
}: DashboardPaperProps): React.ReactElement => {
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
};
