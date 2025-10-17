import { ReactElement, useState } from 'react';
import moment from 'moment';
import styled, { css } from 'styled-components';
import { IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMoreRounded';
import Collapse from '@mui/material/Collapse';
import { ActivityLogEntry } from './types';
import { headCells } from './headCells';
import { ButtonPlaceHolder, Cell, Row } from './TableStyledComponents';

const ButtonContainer = styled.div`
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const CollapseContainer = styled(Collapse)`
  background-color: #fafafa;
`;

const StyledIconButton = styled(IconButton)<{ expanded: boolean }>`
  transform: rotate(0deg);
  transition: ${({ theme }) =>
    theme.transitions.create('transform', { duration: 400 })};
  ${({ expanded }) =>
    expanded &&
    css`
      transform: rotate(180deg);
    `}
`;

interface LogRowProps {
  logEntry: ActivityLogEntry;
}

const formatted = (value): string => {
  const timeWithTimeZoneRegex = /(\d{2}:\d{2}:\d{2})([+-])(\d{2}):(\d{2})$/;
  if (timeWithTimeZoneRegex.test(value)) {
    return value.replace(timeWithTimeZoneRegex, '');
  }
  return value;
};

export const LogRow = ({ logEntry }: LogRowProps): ReactElement => {
  const { changes } = logEntry;
  const [expanded, setExpanded] = useState(false);

  if (!changes) return null;

  const keys = Object.keys(changes);
  const { length } = keys;

  if (length === 1) {
    return (
      <Row role="checkbox" data-cy="log-row">
        <Cell weight={headCells[0].weight} data-cy="timestamp-cell">
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight} data-cy="user-cell">
          {logEntry.userDisplayName || logEntry.user || null}
        </Cell>
        <Cell weight={headCells[2].weight} data-cy="change-key-cell">
          {keys[0]}
        </Cell>
        <Cell weight={headCells[3].weight} data-cy="from-value-cell">
          {formatted(changes[keys[0]].from)}
        </Cell>
        <Cell weight={headCells[4].weight} data-cy="to-value-cell">
          {formatted(changes[keys[0]].to)}
        </Cell>
        <ButtonPlaceHolder />
      </Row>
    );
  }
  return (
    <>
      <Row
        onClick={() => setExpanded(!expanded)}
        hover
        data-cy={`log-row-${logEntry.id}`}
      >
        <Cell weight={headCells[0].weight} data-cy="timestamp-cell">
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight} data-cy="user-cell">
          {logEntry.userDisplayName || logEntry.user || null}
        </Cell>
        <Cell weight={headCells[2].weight} data-cy="change-type-cell">
          Multiple
        </Cell>
        <Cell weight={headCells[3].weight} />
        <Cell weight={headCells[4].weight} />
        <ButtonContainer>
          <StyledIconButton
            expanded={expanded}
            onClick={() => setExpanded(!expanded)}
            data-cy="expand-collapse-button"
          >
            <ExpandMoreIcon />
          </StyledIconButton>
        </ButtonContainer>
      </Row>

      <CollapseContainer in={expanded} data-cy="collapse-container">
        {keys.map((key) => (
          <Row key={`${logEntry.id}${key}`} data-cy={`detail-row-${key}`}>
            <Cell weight={headCells[0].weight} />
            <Cell weight={headCells[1].weight} />
            <Cell weight={headCells[2].weight} data-cy="detail-key-cell">
              {key}
            </Cell>
            <Cell weight={headCells[3].weight} data-cy="detail-from-value-cell">
              {formatted(changes[key].from)}
            </Cell>
            <Cell weight={headCells[4].weight} data-cy="detail-to-value-cell">
              {formatted(changes[key].to)}
            </Cell>
            <ButtonPlaceHolder />
          </Row>
        ))}
      </CollapseContainer>
    </>
  );
};
