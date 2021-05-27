/* eslint-disable prefer-template */
import React, {ReactElement, useState} from 'react';
import moment from 'moment';
import styled from 'styled-components';
import {IconButton, makeStyles} from '@material-ui/core';
import clsx from 'clsx';
import ExpandMore from '@material-ui/icons/ExpandMoreRounded';
import Collapse from '@material-ui/core/Collapse';
import {Link} from 'react-router-dom';
import {AllLogEntriesQuery, LogEntryAction,} from '../../../__generated__/graphql';
import {MiśTheme} from '../../../theme';
import {ButtonPlaceHolder, Cell, Row,} from '../../../components/ActivityLogTable/TableStyledComponents';
import {Dashable} from '../../../components/Dashable';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {headCells} from './MainActivityLogTableHeadCells';

const ButtonContainer = styled.div`
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;
//random color chosen by Przemek
const CollapseContainer = styled(Collapse)`
  background-color: #fafafa;
`;
const StyledLink = styled(Link)`
  color: #000;
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

function snakeToFieldReadable(str: string): string {
  if (!str) {
    return str;
  }
  return str.replace(/([-_][a-z])/g, (group) =>
    group.replace('-', ' ').replace('_', ' '),
  );
}
interface ObjectRepresentationsProps {
  logEntry: AllLogEntriesQuery['allLogEntries']['edges'][number]['node'];
}

function ObjectRepresentations({
  logEntry,
}: ObjectRepresentationsProps): ReactElement {
  const businessArea = useBusinessArea();
  const id = logEntry.objectId;
  const { model } = logEntry.contentType;
  const modelToUrlDict = {
    program: `/${businessArea}/programs/${btoa('ProgramNode:' + id)}`,
    targetpopulation: `/${businessArea}/target-population/${btoa(
      'TargetPopulationNode:' + id,
    )}`,
    grievanceticket: `/${businessArea}/grievance-and-feedback/${btoa(
      'GrievanceTicketNode:' + id,
    )}`,
    household: `/${businessArea}/population/household/${btoa(
      'HouseholdNode:' + id,
    )}`,
    individual: `/${businessArea}/population/individuals/${btoa(
      'IndividualNode:' + id,
    )}`,
    registrationdataimport: `/${businessArea}/registration-data-import/${btoa(
      'RegistrationDataImportNode:' + id,
    )}`,
    cashplanpaymentverification: `/${businessArea}/csh-payment-verification/${btoa(
      'CashPlanPaymentVerificationNode:' + id,
    )}`,
    paymentverification: `/${businessArea}/verification-records/${btoa(
      'PaymentVerificationNode:' + id,
    )}`,
  };
  if (
    !(model in modelToUrlDict) ||
    logEntry.action === LogEntryAction.Delete ||
    logEntry.action === LogEntryAction.SoftDelete
  ) {
    return <>{logEntry.objectRepr}</>;
  }
  return (
    <StyledLink to={modelToUrlDict[model]}>{logEntry.objectRepr}</StyledLink>
  );
}

interface LogRowProps {
  logEntry: AllLogEntriesQuery['allLogEntries']['edges'][number]['node'];
  actionChoicesDict: { [id: string]: string };
}

export function MainActivityLogTableRow({
  logEntry,
  actionChoicesDict,
}: LogRowProps): ReactElement {
  const changes = logEntry.changes || {};
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles({});
  const keys = Object.keys(changes);
  const { length } = keys;
  if (length <= 1) {
    return (
      <Row role='checkbox'>
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.user
            ? `${logEntry.user.firstName} ${logEntry.user.lastName}`
            : 'System'}
        </Cell>
        <Cell weight={headCells[2].weight}>{logEntry.contentType.name}</Cell>
        <Cell weight={headCells[3].weight}>
          <ObjectRepresentations logEntry={logEntry} />
        </Cell>
        <Cell weight={headCells[4].weight}>
          {actionChoicesDict[logEntry.action]}
        </Cell>
        <Cell weight={headCells[5].weight}>
          <Dashable>{snakeToFieldReadable(keys[0])}</Dashable>
        </Cell>
        <Cell weight={headCells[6].weight}>
          <Dashable>{changes[keys[0]]?.from}</Dashable>
        </Cell>
        <Cell weight={headCells[7].weight}>
          <Dashable>{changes[keys[0]]?.to}</Dashable>
        </Cell>
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
            : 'System'}
        </Cell>
        <Cell weight={headCells[2].weight}>{logEntry.contentType.name}</Cell>
        <Cell weight={headCells[3].weight}>
          <ObjectRepresentations logEntry={logEntry} />
        </Cell>
        <Cell weight={headCells[4].weight}>
          {actionChoicesDict[logEntry.action]}
        </Cell>
        <Cell weight={headCells[5].weight}>Multiple</Cell>
        <Cell />
        <Cell />
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
              <Cell weight={headCells[2].weight} />
              <Cell weight={headCells[3].weight} />
              <Cell weight={headCells[4].weight} />
              <Cell weight={headCells[5].weight}>
                {snakeToFieldReadable(key)}
              </Cell>
              <Cell weight={headCells[6].weight}>
                <Dashable>{changes[key].from}</Dashable>
              </Cell>
              <Cell weight={headCells[7].weight}>
                <Dashable>{changes[key].to}</Dashable>
              </Cell>
              <ButtonPlaceHolder />
            </Row>
          );
        })}
      </CollapseContainer>
    </>
  );
}
