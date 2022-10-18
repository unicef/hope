import { Radio } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { BlackLink } from '../../../components/core/BlackLink';
import { StatusBox } from '../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
} from '../../../utils/utils';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../../__generated__/graphql';

interface LookUpProgrammesTableRowProps {
  program: ProgramNode;
  choicesData: ProgrammeChoiceDataQuery;
  radioChangeHandler: (program) => void;
  selectedProgram: string;
}

export const LookUpProgrammesTableRow = ({
  program,
  choicesData,
  radioChangeHandler,
  selectedProgram,
}: LookUpProgrammesTableRowProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const programDetailsPath = `/${businessArea}/programs/${program.id}`;
  const handleClick = (): void => {
    radioChangeHandler(program.id);
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
      <TableCell padding='checkbox'>
        <Radio
          color='primary'
          checked={selectedProgram === program.id}
          onChange={() => {
            radioChangeHandler(program.id);
          }}
          value={program.id}
          name='radio-button-program'
          inputProps={{ 'aria-label': program.id }}
          data-cy='input-radio-program'
        />
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={programDetailsPath}>{program.name}</BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={program.status}
          statusToColor={programStatusToColor}
        />
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
};
