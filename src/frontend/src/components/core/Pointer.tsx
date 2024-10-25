import { ReactElement } from 'react';
import styled from 'styled-components';

const PointerCursor = styled.span`
  cursor: pointer;
`;
export function Pointer({ children }): ReactElement {
  return <PointerCursor>{children}</PointerCursor>;
}
