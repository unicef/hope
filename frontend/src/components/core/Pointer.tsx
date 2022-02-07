import React from 'react';
import styled from 'styled-components';

const PointerCursor = styled.span`
  cursor: pointer;
`;
export const Pointer = ({ children }): React.ReactElement => {
  return <PointerCursor>{children}</PointerCursor>;
};
