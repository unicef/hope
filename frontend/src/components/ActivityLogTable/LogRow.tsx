import React, { ReactElement, useState } from 'react';
import moment from 'moment';
import styled from 'styled-components';
import { IconButton, makeStyles } from '@material-ui/core';
import clsx from 'clsx';
import ExpandMore from '@material-ui/icons/ExpandMoreRounded';
import Collapse from '@material-ui/core/Collapse';
import { LogEntryObject } from '../../__generated__/graphql';
import { MiśTheme } from '../../theme';
import { headCells } from './headCels';
import { ButtonPlaceHolder, Cell, Row } from './TableStyledComponents';

const ButtonContainer = styled.div`
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;
//random color chosen by Przemek
const CollapseContainer = styled(Collapse)`
  background-color: #fafafa;
`;
// transitions not working in styled components
const useStyles = makeStyles((theme: MiśTheme) => ({
  expanded: {},
  expandIcon: {
    transform: 'rotate(0deg)',
    transition: theme.transitions.create('transform', { duration: 400 }),
    '&$expanded': {
      transform: 'rotate(180deg)',
    },
  },
}));

interface LogRowProps {
  logEntry: LogEntryObject;
}

export function LogRow({ logEntry }: LogRowProps): ReactElement {
  const changes = JSON.parse(logEntry.changesDisplayDict);
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles({});
  const keys = Object.keys(changes);
  const { length } = keys;
  if (length === 1) {
    return (
      <Row role='checkbox'>
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.actor
            ? `${logEntry.actor.firstName} ${logEntry.actor.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>{keys[0].toUpperCase()}</Cell>
        <Cell weight={headCells[3].weight}>{changes[keys[0]][0]}</Cell>
        <Cell weight={headCells[4].weight}>{changes[keys[0]][1]}</Cell>
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
          {logEntry.actor
            ? `${logEntry.actor.firstName} ${logEntry.actor.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>Multiple</Cell>
        <Cell weight={headCells[3].weight} />
        <Cell weight={headCells[4].weight} />
        <ButtonContainer>
          <IconButton
            className={clsx(classes.expandIcon, {
              [classes.expanded]: expanded,
            })}
            onClick={() => setExpanded(!expanded)}
          >
            <ExpandMore />
          </IconButton>
        </ButtonContainer>
      </Row>

      <CollapseContainer in={expanded}>
        {keys.map((key) => {
          return (
            <Row key={logEntry + key}>
              <Cell weight={headCells[0].weight} />
              <Cell weight={headCells[1].weight} />
              <Cell weight={headCells[2].weight}>{key}</Cell>
              <Cell weight={headCells[3].weight}>{changes[key][0]}</Cell>
              <Cell weight={headCells[4].weight}>{changes[key][1]}</Cell>
              <ButtonPlaceHolder />
            </Row>
          );
        })}
      </CollapseContainer>
    </>
  );
}
