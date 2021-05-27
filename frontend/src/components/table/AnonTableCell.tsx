import {TableCell} from '@material-ui/core';
import React from 'react';
import {hasPermissions, PERMISSIONS} from '../../config/permissions';
import {usePermissions} from '../../hooks/usePermissions';
import {anon} from '../../utils/utils';

export const AnonTableCell = ({ children, ...props }): React.ReactElement => {
  const permissions = usePermissions();
  if (permissions === null) return null;

  const shouldAnonymize = !hasPermissions(
    PERMISSIONS.ALL_VIEW_PII_DATA_ON_LISTS,
    permissions,
  );
  return (
    <TableCell align='left' {...props}>
      {anon(children, shouldAnonymize)}
    </TableCell>
  );
};
