import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  ProgramNode,
  ProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';
import { UniversalMoment } from '../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface ProgrammesTableRowProps {
  program: ProgramNode;
  choicesData: ProgrammeChoiceDataQuery;
}

export function ProgrammesTableRow({
  program,
  choicesData,
}: ProgrammesTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/programs/${program.id}`;
    history.push(path);
  };

  const programFreqOfPayChoiceDict = choicesToDict(
    choicesData.programFrequencyOfPaymentsChoices,
  );
  const programScopeChoiceDict = choicesToDict(choicesData.programScopeChoices);
  const programSectorChoiceDict = choicesToDict(
    choicesData.programSectorChoices,
  );
  const programStatusChoiceDict = choicesToDict(
    choicesData.programStatusChoices,
  );
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={program.id}
    >
      <TableCell align='left'>{program.name}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={program.status}
            statusToColor={programStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{program.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{program.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {programFreqOfPayChoiceDict[program.frequencyOfPayments]}
      </TableCell>
      <TableCell align='right'>{formatCurrency(program.budget)}</TableCell>
      <TableCell align='right'>{program.populationGoal}</TableCell>
      <TableCell align='right'>{program.totalNumberOfHouseholds}</TableCell>
      <TableCell align='left'>
        {programSectorChoiceDict[program.sector]}
      </TableCell>
    </ClickableTableRow>
  );
}
