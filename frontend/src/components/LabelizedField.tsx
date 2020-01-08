import React from 'react';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import { MiśTheme, theme as themeObj } from '../theme';
import styled from 'styled-components';

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

export function LabelizedField({ value, children, label }: Props) {
  return (
    <div>
      <Label color='textSecondary'>{label}</Label>
      <div>{children || <Value color='textSecondary'>{value}</Value>}</div>
    </div>
  );
}
