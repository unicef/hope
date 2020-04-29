import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import moment from 'moment';
import { ImportedIndividualMinimalFragment } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../../utils/utils';
import { Missing } from '../../../../components/Missing';

interface ImportedIndividualsTableRowProps {
  individual: ImportedIndividualMinimalFragment;
}

export function ImportedIndividualsTableRow({
  individual,
}: ImportedIndividualsTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/individual/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow hover onClick={handleClick} key={individual.id}>
      <TableCell align='left'>{decodeIdString(individual.id)}</TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        {moment(individual.birthDate).format('DD MMM YYYY')}
      </TableCell>
      <TableCell align='left'>{individual.sex}</TableCell>
    </ClickableTableRow>
  );
}
