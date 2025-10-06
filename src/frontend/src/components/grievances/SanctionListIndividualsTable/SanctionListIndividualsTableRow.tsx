import { TableCell, TableRow } from '@mui/material';
import moment from 'moment';
import { DATE_FORMAT } from '../../../config';
import { SanctionListIndividual } from '@restgenerated/models/SanctionListIndividual';
import { ReactElement } from 'react';

export function SanctionListIndividualsTableRow({
  individual,
}: {
  individual: SanctionListIndividual;
}): ReactElement {
  return (
    <TableRow>
      <TableCell align="left">{individual.referenceNumber}</TableCell>
      <TableCell align="left">{individual.fullName}</TableCell>
      <TableCell align="left">
        {individual.datesOfBirth
          .map((item) => moment(item.date).format(DATE_FORMAT))
          .join(', ') || '-'}
      </TableCell>
      <TableCell align="left">
        {individual.documents.map((item) => item.documentNumber).join(', ') ||
          '-'}
      </TableCell>
    </TableRow>
  );
}
