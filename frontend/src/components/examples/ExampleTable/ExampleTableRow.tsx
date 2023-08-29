import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { BlackLink } from '../../core/BlackLink';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';

interface ExampleTableRowProps {
  prop?: string;
  canViewDetails?: boolean;
}

export const ExampleTableRow = ({
  canViewDetails,
}: ExampleTableRowProps): React.ReactElement => {
  const detailsPath = '';
  const handleRowClick = (): void => {
    //eslint-disable-next-line no-console
    console.log('handleRowClick');
  };
  return (
    <ClickableTableRow onClick={handleRowClick} hover role='checkbox' key={0}>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={detailsPath}>example</BlackLink>
        ) : (
          'example'
        )}
      </TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>
        <UniversalMoment>date</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
