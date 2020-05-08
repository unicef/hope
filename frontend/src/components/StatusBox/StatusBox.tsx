import React from 'react';
import styled from 'styled-components';
import { theme as themeObj } from '../../theme';
import { opacityToHex } from '../../utils/utils';

interface Props {
  status: string;
  statusToColor: (theme: typeof themeObj, status: string) => string;
  statusNameMapping?: Function;
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
  padding: ${({ theme }) => theme.spacing(1)}px;
  text-align: center;
`;

export function StatusBox({
  status,
  statusToColor,
  statusNameMapping,
}: Props): React.ReactElement {
  const underscoreRemoveRegex = /_/g;
  return (
    <StatusBoxContainer
      status={status}
      statusToColor={statusToColor}
      data-cy='program-status-container'
    >
      {statusNameMapping
        ? statusNameMapping(status.replace(underscoreRemoveRegex, ' '))
        : status.replace(underscoreRemoveRegex, ' ')}
    </StatusBoxContainer>
  );
}
