import { Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { AllProgramsQuery, ProgrammeChoiceDataQuery } from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
} from '@utils/utils';

interface LookUpProgrammesTableRowSurveysProps {
  program: AllProgramsQuery['allPrograms']['edges'][number]['node'];
  choicesData: ProgrammeChoiceDataQuery;
  radioChangeHandler: (program) => void;
  selectedProgram: string;
}

export function LookUpProgrammesTableRowSurveys({
  program,
  choicesData,
  radioChangeHandler,
  selectedProgram,
}: LookUpProgrammesTableRowSurveysProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const programDetailsPath = `/${baseUrl}/details/${program.id}`;
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
      role="checkbox"
      key={program.id}
    >
      <TableCell padding="checkbox">
        <Radio
          color="primary"
          checked={selectedProgram === program.id}
          onChange={() => {
            radioChangeHandler(program.id);
          }}
          value={program.id}
          name="radio-button-program"
          inputProps={{ 'aria-label': program.id }}
          data-cy="input-radio-program"
        />
      </TableCell>
      <TableCell align="left">
        <BlackLink to={programDetailsPath}>{program.name}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={program.status}
          statusToColor={programStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{program.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{program.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        {programSectorChoiceDict[program.sector]}
      </TableCell>
      <TableCell align="right">
        {program.totalNumberOfHouseholdsWithTpInProgram}
      </TableCell>
      <TableCell align="right">{formatCurrency(program.budget)}</TableCell>
    </ClickableTableRow>
  );
}
