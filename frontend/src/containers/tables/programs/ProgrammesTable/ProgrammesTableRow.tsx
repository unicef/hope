import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
<<<<<<< HEAD:frontend/src/containers/tables/programs/ProgrammesTable/ProgrammesTableRow.tsx
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
=======
import {
  AllProgramsQuery,
  ProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { BlackLink } from '../../../components/core/BlackLink';
import { StatusBox } from '../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
>>>>>>> cb4319bb4d0d695656d0ec4956559438fdd72937:frontend/src/containers/tables/ProgrammesTable/ProgrammesTableRow.tsx
import {
  choicesToDict,
  formatCurrency,
  programStatusToColor,
<<<<<<< HEAD:frontend/src/containers/tables/programs/ProgrammesTable/ProgrammesTableRow.tsx
} from '../../../../utils/utils';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
=======
} from '../../../utils/utils';
>>>>>>> cb4319bb4d0d695656d0ec4956559438fdd72937:frontend/src/containers/tables/ProgrammesTable/ProgrammesTableRow.tsx

interface ProgrammesTableRowProps {
  program: AllProgramsQuery['allPrograms']['edges'][number]['node'];
  choicesData: ProgrammeChoiceDataQuery;
}

export const ProgrammesTableRow = ({
  program,
  choicesData,
}: ProgrammesTableRowProps): React.ReactElement => {
  const history = useHistory();
  const { baseUrl } = useBaseUrl();
  const programDetailsPath = `/${baseUrl}/details/${program.id}`;
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
      data-cy={`table-row-${program.name}`}
    >
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
