import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../theme';

const Label = styled.span`
  ${({ theme }: { theme: MiśTheme }) => theme.styledMixins.label}
`;

const Value = styled.span`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
`;

export interface Props {
  value?: React.ReactNode;
  children?: React.ReactElement;
  label: string;
}

export function LabelizedField({
  value,
  children,
  label,
}: Props): React.ReactElement {
  return (
    <div>
      <Label color='textSecondary'>{label}</Label>
      <div>{children || <Value color='textSecondary'>{value}</Value>}</div>
    </div>
  );
}
