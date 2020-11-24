import React, { ReactElement, useEffect, useState } from 'react';
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
  useApproveIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import mapKeys from 'lodash/mapKeys';
import { Checkbox, makeStyles } from '@material-ui/core';
import { LoadingComponent } from '../LoadingComponent';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';

const TableCellStroke = styled(TableCell)`
  &::before {
    content: ' ';
    position: absolute;
    width: 100%;
    border-bottom: red solid 1px;
    top: calc(50% - 1px);
    left: 0;
  }
  & {
    position: relative;
  }
`;

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
        field.choices.find((item) => item.value === value)?.labelEn || '-';
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
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const { documents } = individualData;
  const documentsToRemove = individualData.documents_to_remove;
  // eslint-disable-next-line no-param-reassign
  delete individualData.documents;
  // eslint-disable-next-line no-param-reassign
  delete individualData.documents_to_remove;
  const entries = Object.entries(individualData);
  useEffect(() => {
    const localSelected = entries
      .filter((row) => {
        const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
          value: string;
          approveStatus: boolean;
        };
        return valueDetails.approveStatus;
      })
      .map((row) => camelCase(row[0]));
    setSelected(localSelected);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket]);

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
  const countriesDict = data.countriesChoices.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.value] = currentValue.name;
      return previousValue;
    },
    {},
  );
  const documentTypeDict = data.documentTypeChoices.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.value] = currentValue.name;
      return previousValue;
    },
    {},
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
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return (
              <TableRow
                role='checkbox'
                aria-checked={isItemSelected}
                key={fieldName}
              >
                <TableCell>
                  <Checkbox
                    onClick={(event) => handleClick(event, fieldName)}
                    color='primary'
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
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
                  <CurrentValue field={field} value={valueDetails.value} />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>ID Type</TableCell>
            <TableCell align='left'>Country</TableCell>
            <TableCell align='left'>Number</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {documents?.map((row, index) => {
            return (
              <TableRow>
                <TableCell align='left'>
                  <Checkbox
                    color='primary'
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                    checked
                    inputProps={{ 'aria-labelledby': 'xd' }}
                  />
                </TableCell>
                <TableCell align='left'>
                  {documentTypeDict[row.value.type]}
                </TableCell>
                <TableCell align='left'>
                  {countriesDict[row.value.country]}
                </TableCell>
                <TableCell align='left'>{row.value.number}</TableCell>
              </TableRow>
            );
          })}
          {documentsToRemove?.map((row, index) => {
            const document = ticket.individualDataUpdateTicketDetails.individual.documents.edges.find(
              (item) => item.node.id === row.value,
            );
            return (
              <TableRow>
                <TableCell align='left'>
                  <Checkbox
                    color='primary'
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                    checked
                    inputProps={{ 'aria-labelledby': 'xd' }}
                  />
                </TableCell>
                <TableCellStroke align='left'>
                  {document.node.type.label}
                </TableCellStroke>
                <TableCellStroke align='left'>
                  {document.node.type.country}
                </TableCellStroke>
                <TableCellStroke align='left'>
                  {document.node.documentNumber}
                </TableCellStroke>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
