import { TableCell, TableRow } from '@mui/material';
import moment from 'moment';
import { DATE_FORMAT } from '../../../config';
import { AllSanctionListIndividualsQuery } from '@generated/graphql';
import { UniversalMoment } from '@core/UniversalMoment';
import { ReactElement } from 'react';

export function SanctionListIndividualsTableRow({
  individual,
}: {
  individual: AllSanctionListIndividualsQuery['allSanctionListIndividuals']['edges'][number]['node'];
}): ReactElement {
  return (
    <TableRow>
      <TableCell align="left">{individual.referenceNumber}</TableCell>
      <TableCell align="left">{individual.fullName}</TableCell>
      <TableCell align="left">
        {individual.datesOfBirth.edges
          .map((item) => moment(item.node.date).format(DATE_FORMAT))
          .join(', ') || '-'}
      </TableCell>
      <TableCell align="left">
        {individual.documents.edges
          .map((item) => item.node.documentNumber)
          .join(', ') || '-'}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{individual.listedOn}</UniversalMoment>
      </TableCell>
    </TableRow>
  );
}
