import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import Table from '@material-ui/core/Table';
import camelCase from 'lodash/camelCase';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import {
  AllAddIndividualFieldsQuery,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';
import { Checkbox, makeStyles } from '@material-ui/core';
import { LoadingComponent } from '../LoadingComponent';

const Capitalize = styled.span`
  text-transform: capitalize;
`;

export interface CurrentValueProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue = value;
  switch (field?.type) {
    case 'SELECT_ONE':
      displayValue =
        field.choices.find((item) => item.value === value).labelEn || '-';
      break;
    case 'BOOL':
      /* eslint-disable-next-line no-nested-ternary */
      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}
interface RequestedIndividualDataChangeTableProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  setFieldValue;
}
export function RequestedIndividualDataChangeTable({
  setFieldValue,
  ticket,
}: RequestedIndividualDataChangeTableProps): ReactElement {
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();
  const [selected, setSelected] = useState([]);
  const { data, loading } = useAllAddIndividualFieldsQuery();

  if (loading) {
    return <LoadingComponent />;
  }

  const fieldsDict = data.allAddIndividualsFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
    {},
  );

  const entries = Object.entries(
    ticket.individualDataUpdateTicketDetails.individualData,
  );

  const handleClick = (event, name) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    setSelected(newSelected);
    setFieldValue('selected', newSelected);
  };

  const isSelected = (name: string): boolean => selected.includes(name);

  return (
    <div>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>Type of Data</TableCell>
            <TableCell align='left'>Current Value</TableCell>
            <TableCell align='left'>New Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map((row, index) => {
            const fieldName = camelCase(row[0]);
            const isItemSelected = isSelected(fieldName);
            const labelId = `enhanced-table-checkbox-${index}`;
            const currentValue =
              ticket.individualDataUpdateTicketDetails.individual[fieldName];
            const field = fieldsDict[row[0]];
            return (
              <TableRow
                onClick={(event) => handleClick(event, fieldName)}
                role='checkbox'
                aria-checked={isItemSelected}
                key={fieldName}
              >
                <TableCell>
                  <Checkbox
                    color='primary'
                    checked={isItemSelected}
                    inputProps={{ 'aria-labelledby': labelId }}
                  />
                </TableCell>
                <TableCell id={labelId} scope='row' align='left'>
                  <Capitalize>{row[0].replaceAll('_', ' ')}</Capitalize>
                </TableCell>
                <TableCell align='left'>
                  <CurrentValue field={field} value={currentValue} />
                </TableCell>
                <TableCell align='left'>
                  <CurrentValue field={field} value={row[1]} />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
