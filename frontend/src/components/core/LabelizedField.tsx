import { TFunctionResult } from 'i18next';
import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';

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
  children?: React.ReactElement | string | number | boolean | TFunctionResult;
  label: string;
  dataCy?: string;
  dashed?: boolean;
}

export function LabelizedField({
  value,
  children,
  label,
  dataCy,
  dashed = true,
}: Props): React.ReactElement {
  let fieldValue;
  if (children !== undefined) {
    fieldValue = children;
  } else {
    fieldValue = value;
  }

  let displayValue = children;

  const shouldDisplayDash = dashed && fieldValue !== 0 && !fieldValue;
  if (shouldDisplayDash) {
    displayValue = '-';
  } else if (children === undefined) {
    displayValue = <Value color='textSecondary'>{value}</Value>;
  }

  return (
    <div data-cy={dataCy && `labelized-field-container-${dataCy}`}>
      <Label color='textSecondary'>{label}</Label>
      <div data-cy={`label-${label}`}>{displayValue}</div>
    </div>
  );
}
