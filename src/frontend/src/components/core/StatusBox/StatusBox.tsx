import styled from 'styled-components';
import { theme as themeObj } from '../../../theme';
import { opacityToHex } from '@utils/utils';
import { ReactElement } from 'react';

interface Props {
  status: string;
  statusToColor: (theme: typeof themeObj, status: string) => string;
  statusNameMapping?: (status: string) => string;
  statusDisplay?: string;
  dataCy?: string;
}
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 300px;
`;

interface StatusBoxContainerProps {
  $status: string;
  $statusToColor: (theme: any, status: string) => string;
  theme: any;
}

const StatusBoxContainer = styled.div<StatusBoxContainerProps>`
  color: ${({ $status, $statusToColor, theme }) =>
    $statusToColor(theme, $status)};
  background-color: ${({ $status, $statusToColor, theme }) =>
    `${$statusToColor(theme, $status)}${opacityToHex(0.15)}`};
  border-radius: 16px;
  font-family: Roboto;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  line-height: 16px;
  padding: 4px;
  text-align: center;
  margin-right: 20px;
`;

export const StatusBox = ({
  status,
  statusToColor,
  statusNameMapping,
  statusDisplay,
  dataCy,
}: Props): ReactElement => {
  const underscoreRemoveRegex = /_/g;
  if (!status) return <>-</>;
  return (
    <StatusContainer>
      <StatusBoxContainer
        className="status-box-container"
        $status={status}
        $statusToColor={statusToColor}
        data-cy={dataCy || 'status-container'}
      >
        {statusNameMapping
          ? statusNameMapping(status)
          : statusDisplay
            ? statusDisplay
            : status?.replace(underscoreRemoveRegex, ' ')}
      </StatusBoxContainer>
    </StatusContainer>
  );
};
