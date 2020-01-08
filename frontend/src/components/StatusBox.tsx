import { makeStyles } from '@material-ui/core/styles';
import { theme as themeObj } from '../theme';
import { opacityToHex } from '../utils/utils';
import React from 'react';
import styled from 'styled-components';

interface Props {
  status: string;
  statusToColor: (theme: typeof themeObj, status: string) => string;
}

const StatusBoxContainer = styled.div`
  color: ${({ status, statusToColor, theme }) => statusToColor(theme, status)};
  background-color: ${({ status, statusToColor, theme }) =>
    `${statusToColor(theme, status)}${opacityToHex(0.15)}`};
  border-radius: 16px;
  font-family: Roboto;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  line-height: 16px;
  padding: 3px;
  text-align: center;
`;

export function StatusBox({ status, statusToColor }: Props) {
  return (
    <StatusBoxContainer status={status} statusToColor={statusToColor}>
      {status}
    </StatusBoxContainer>
  );
}
