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
import { BlackLink } from '../../../components/BlackLink';

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
  const programDetailsPath = `/${businessArea}/programs/${program.id}`;
  const handleClick = (): void => {
    history.push(programDetailsPath);
  };

  const programSectorChoiceDict = choicesToDict(
    choicesData.programSectorChoices,
  );

  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={program.id}
    >
      <TableCell align='left'>
        <BlackLink to={programDetailsPath}>{program.name}</BlackLink>
      </TableCell>
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
        {programSectorChoiceDict[program.sector]}
      </TableCell>
      <TableCell align='right'>{program.totalNumberOfHouseholds}</TableCell>
      <TableCell align='right'>{formatCurrency(program.budget)}</TableCell>
    </ClickableTableRow>
  );
}
