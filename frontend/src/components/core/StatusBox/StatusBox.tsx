import React from 'react';
import styled from 'styled-components';
import { theme as themeObj } from '../../../theme';
import { opacityToHex } from '../../../utils/utils';

interface Props {
  status: string;
  statusToColor: (theme: typeof themeObj, status: string) => string;
  statusNameMapping?: Function;
  dataCy?: string;
}
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

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
  margin-right: 20px;
`;

export function StatusBox({
  status,
  statusToColor,
  statusNameMapping,
  dataCy,
}: Props): React.ReactElement {
  const underscoreRemoveRegex = /_/g;
  if (!status) return <>-</>;
  return (
    <StatusContainer>
      <StatusBoxContainer
        status={status}
        statusToColor={statusToColor}
        data-cy={dataCy ? dataCy : 'status-container'}
      >
        {statusNameMapping
          ? statusNameMapping(status)
          : status?.replace(underscoreRemoveRegex, ' ')}
      </StatusBoxContainer>
    </StatusContainer>
  );
}
