import { ReactNode, ReactElement } from 'react';
import styled, { css } from 'styled-components';

interface TabPanelProps {
  children: ReactNode;
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
}: TabPanelProps): ReactElement {
  return (
    <StyledDiv index={index} value={value}>
      {children}
    </StyledDiv>
  );
}
