import { IconButton, makeStyles } from '@mui/material';
import Collapse from '@mui/material/Collapse';
import ExpandMoreIcon from '@mui/icons-material/ExpandMoreRounded';
import clsx from 'clsx';
import moment from 'moment';
import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../../theme';
import { PaymentVerificationLogEntryNode } from '../../../__generated__/graphql';
import { headCells } from './headCells';
import { ButtonPlaceHolder, Cell, Row } from './TableStyledComponents';

const ButtonContainer = styled.div`
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;
// random color chosen by Przemek
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
  logEntry: PaymentVerificationLogEntryNode;
}

export function LogRow({ logEntry }: LogRowProps): ReactElement {
  const { changes } = logEntry;
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles({});
  const keys = Object.keys(changes);
  const { length } = keys;
  if (length === 1) {
    return (
      <Row role="checkbox">
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.user
            ? `${logEntry.user.firstName} ${logEntry.user.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>
          {logEntry.contentObject?.unicefId}
        </Cell>
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
          {logEntry.user
            ? `${logEntry.user.firstName} ${logEntry.user.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>
          {logEntry.contentObject?.unicefId}
        </Cell>
        <Cell weight={headCells[3].weight}>Multiple</Cell>
        <Cell weight={headCells[4].weight} />
        <Cell weight={headCells[5].weight} />
        <ButtonContainer>
          <IconButton
            className={clsx(classes.expandIcon, {
              [classes.expanded]: expanded,
            })}
            onClick={() => setExpanded(!expanded)}
          >
            <ExpandMoreIcon />
          </IconButton>
        </ButtonContainer>
      </Row>

      <CollapseContainer in={expanded}>
        {keys.map((key) => (
          <Row key={logEntry + key}>
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
}
