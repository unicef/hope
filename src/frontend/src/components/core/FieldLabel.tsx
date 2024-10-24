import { ReactElement } from 'react';
import styled from 'styled-components';

const Label = styled.span`
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
`;

interface FieldLabelProps {
  children: string;
}
export function FieldLabel({ children }: FieldLabelProps): ReactElement {
  return <Label>{children}</Label>;
}
