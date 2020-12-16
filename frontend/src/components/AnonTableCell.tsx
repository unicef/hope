import { TableCell } from '@material-ui/core';
import React from 'react';
import { anon } from '../utils/utils';

export const AnonTableCell = ({
  anonymize,
  children,
  ...props
}): React.ReactElement => {
  return <TableCell {...props}>{anon(children, anonymize)}</TableCell>;
};
