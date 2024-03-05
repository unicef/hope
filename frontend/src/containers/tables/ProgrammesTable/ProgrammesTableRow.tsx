import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
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

interface ProgrammesTableRowProps {
  program: AllProgramsQuery['allPrograms']['edges'][number]['node'];
  choicesData: ProgrammeChoiceDataQuery;
}

export function ProgrammesTableRow({
  program,
  choicesData,
}: ProgrammesTableRowProps): React.ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const programDetailsPath = `/${baseUrl}/details/${program.id}`;
  const handleClick = (): void => {
    navigate(programDetailsPath);
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
      data-cy={`table-row-${program.name}`}
    >
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
      <TableCell align="right">{program.totalNumberOfHouseholds}</TableCell>
      <TableCell align="right">{formatCurrency(program.budget)}</TableCell>
    </ClickableTableRow>
  );
}
