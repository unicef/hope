import { ReactElement, useState } from 'react';
import moment from 'moment';
import styled, { css } from 'styled-components';
import { IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMoreRounded';
import Collapse from '@mui/material/Collapse';
import { headCells } from './headCells';
import { ButtonPlaceHolder, Cell, Row } from './TableStyledComponents';
import { LogEntry } from '@restgenerated/models/LogEntry';

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
  logEntry: LogEntry;
}

export const LogRow = ({ logEntry }: LogRowProps): ReactElement => {
  const { changes } = logEntry;
  const [expanded, setExpanded] = useState(false);
  const keys = Object.keys(changes);
  const { length } = keys;
  if (length === 1) {
    return (
      <Row role="checkbox">
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.user ? `${logEntry.user}` : null}
        </Cell>
        <Cell weight={headCells[2].weight}>{logEntry.objectId}</Cell>
        <Cell weight={headCells[3].weight}>{changes[keys[0]].from}</Cell>
        <Cell weight={headCells[4].weight}>{changes[keys[0]].to}</Cell>
        <ButtonPlaceHolder />
      </Row>
    );
  }
  return (
    <>
      <Row onClick={() => setExpanded(!expanded)} hover>
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.user ? `${logEntry.user}` : null}
        </Cell>
        <Cell weight={headCells[2].weight}>{logEntry.objectId}</Cell>
        <Cell weight={headCells[3].weight}>Multiple</Cell>
        <Cell weight={headCells[4].weight} />
        <Cell weight={headCells[5].weight} />
        <ButtonContainer>
          <StyledIconButton
            expanded={expanded}
            onClick={() => setExpanded(!expanded)}
          >
            <ExpandMoreIcon />
          </StyledIconButton>
        </ButtonContainer>
      </Row>

      <CollapseContainer in={expanded}>
        {keys.map((key) => (
          <Row key={logEntry.objectId}>
            <Cell weight={headCells[0].weight} />
            <Cell weight={headCells[1].weight} />
            <Cell weight={headCells[2].weight} />
            <Cell weight={headCells[3].weight}>{key}</Cell>
            <Cell weight={headCells[4].weight}>{changes[key].from}</Cell>
            <Cell weight={headCells[5].weight}>{changes[key].to}</Cell>
            <ButtonPlaceHolder />
          </Row>
        ))}
      </CollapseContainer>
    </>
  );
};
