import * as React from 'react';
import styled, { css } from 'styled-components';

interface TabPanelProps {
  children: React.ReactNode;
  index: number;
  value: number;
}

const StyledDiv = styled.div<TabPanelProps>`
  ${({ index, value }) =>
    index !== value &&
    css`
      display: none;
    `}
`;

export function TabPanel({
  children,
  index,
  value,
}: TabPanelProps): React.ReactElement {
  return (
    <StyledDiv index={index} value={value}>
      {children}
    </StyledDiv>
  );
}
