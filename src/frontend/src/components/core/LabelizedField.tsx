import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { ReactNode, ReactElement } from 'react';

const Label = styled.span`
  ${({ theme }: { theme: MiśTheme }) => theme.styledMixins.label}
`;

const Value = styled.span`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
  overflow-wrap: break-word;
`;

export interface Props {
  value?: ReactNode;
  children?: ReactNode;
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
}: Props): ReactElement {
  let fieldValue;
  if (children !== undefined) {
    fieldValue = children;
  } else {
    fieldValue = value;
  }

  let displayValue;

  const shouldDisplayDash = dashed && fieldValue !== 0 && !fieldValue;
  if (shouldDisplayDash) {
    displayValue = '-';
  } else {
    displayValue = <Value color="textSecondary">{fieldValue}</Value>;
  }

  return (
    <div data-cy={dataCy && `labelized-field-container-${dataCy}`}>
      <Label color="textSecondary">{label}</Label>
      <div data-cy={`label-${label}`}>{displayValue}</div>
    </div>
  );
}
