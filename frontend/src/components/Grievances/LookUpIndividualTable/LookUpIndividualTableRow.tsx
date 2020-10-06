import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { IndividualNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { getAgeFromDob, sexToCapitalize } from '../../../utils/utils';
import { ClickableTableRow } from '../../table/ClickableTableRow';

interface LookUpIndividualTableRowProps {
  individual: IndividualNode;
}

export function LookUpIndividualTableRow({
  individual,
}: LookUpIndividualTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  let age: number | string = 'N/A';
  if (individual.birthDate) {
    age = getAgeFromDob(individual.birthDate);
  }
  const handleClick = (): void => {
    const path = `/${businessArea}/population/individuals/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={individual.id}
    >
      <TableCell align='left'>{individual.unicefId}</TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>
        {individual.household ? individual.household.unicefId : ''}
      </TableCell>
      <TableCell align='right'>{age}</TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>
        {individual.household?.adminArea?.title}
      </TableCell>
    </ClickableTableRow>
  );
}
