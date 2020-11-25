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
import {
  Box,
  Button,
  Checkbox,
  makeStyles,
  Typography,
} from '@material-ui/core';
import { LoadingComponent } from '../LoadingComponent';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useArrayToDict } from '../../hooks/useArrayToDict';

const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

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
  values;
}
export function RequestedIndividualDataChangeTable({
  setFieldValue,
  ticket,
  values,
}: RequestedIndividualDataChangeTableProps): ReactElement {
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();

  const selectedBioData = values.selected;
  const { selectedDocuments } = values;
  const { selectedDocumentsToRemove } = values;
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

  const fieldsDict = useArrayToDict(
    data?.allAddIndividualsFieldsAttributes,
    'name',
    '*',
  );
  const countriesDict = useArrayToDict(data?.countriesChoices, 'value', 'name');
  const documentTypeDict = useArrayToDict(
    data?.documentTypeChoices,
    'value',
    'name',
  );

  if (loading || !fieldsDict || !countriesDict || !documentTypeDict) {
    return <LoadingComponent />;
  }

  const handleSelectBioData = (name, selected) => {
    const newSelected = [...selectedBioData];
    const selectedIndex = newSelected.indexOf(name);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(name);
    }
    setFieldValue('selected', newSelected);
  };
  const handleSelectDocument = (documentIndex, selected) => {
    const newSelected = [...selectedDocuments];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocuments', newSelected);
  };

  const handleSelectDocumentToRemove = (documentIndex, selected) => {
    const newSelected = [...selectedDocumentsToRemove];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocumentsToRemove', newSelected);
  };

  const isSelected = (name: string): boolean => selectedBioData.includes(name);

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
                    onChange={(event) =>
                      handleSelectBioData(fieldName, event.target.checked)
                    }
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
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Document Changes</Typography>
        </Box>
      </Title>
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
                    onChange={(event) => {
                      handleSelectDocument(index, event.target.checked);
                    }}
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                    checked={selectedDocuments.includes(index)}
                    inputProps={{ 'aria-labelledby': 'selected' }}
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
                    onChange={(event) => {
                      handleSelectDocumentToRemove(index, event.target.checked);
                    }}
                    color='primary'
                    disabled={
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                    checked={selectedDocumentsToRemove.includes(index)}
                    inputProps={{ 'aria-labelledby': 'xd' }}
                  />
                </TableCell>
                <TableCellStroke align='left'>
                  {document?.node?.type?.label || '-'}
                </TableCellStroke>
                <TableCellStroke align='left'>
                  {document?.node?.type?.country || '-'}
                </TableCellStroke>
                <TableCellStroke align='left'>
                  {document?.node?.documentNumber || '-'}
                </TableCellStroke>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
