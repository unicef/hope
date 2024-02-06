import React from 'react';
import styled from 'styled-components';

const PointerCursor = styled.span`
  cursor: pointer;
`;
export function Pointer({ children }): React.ReactElement {
  return <PointerCursor>{children}</PointerCursor>;
}
