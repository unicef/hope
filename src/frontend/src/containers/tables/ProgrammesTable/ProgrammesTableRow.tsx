import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import withErrorBoundary from '@components/core/withErrorBoundary';
import {
  AllProgramsForTableQuery,
  ProgrammeChoiceDataQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface ProgrammesTableRowProps {
  program: AllProgramsForTableQuery['allPrograms']['edges'][number]['node'];
  choicesData: ProgrammeChoiceDataQuery;
}

function ProgrammesTableRow({
  program,
  choicesData,
}: ProgrammesTableRowProps): ReactElement {
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
    <>
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
    </>
  );
}
export default withErrorBoundary(ProgrammesTableRow, 'ProgrammesTableRow');
