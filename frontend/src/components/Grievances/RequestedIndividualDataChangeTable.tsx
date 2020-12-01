import React, { ReactElement } from 'react';
import styled from 'styled-components';
import Table from '@material-ui/core/Table';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import camelCase from 'lodash/camelCase';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import mapKeys from 'lodash/mapKeys';
import { Box, Checkbox, makeStyles, Typography } from '@material-ui/core';
import { LoadingComponent } from '../LoadingComponent';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useArrayToDict } from '../../hooks/useArrayToDict';
import {
  AllAddIndividualFieldsQuery,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';

const Title = styled.div`
  padding-top: ${({ theme }) => theme.spacing(4)}px;
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const Capitalize = styled.span`
  text-transform: capitalize;
`;
const GreenIcon = styled.div`
  color: #28cb15;
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
  isEdit;
}
export function RequestedIndividualDataChangeTable({
  setFieldValue,
  ticket,
  values,
  isEdit,
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
  const documents = individualData?.documents;
  const previousDocuments = individualData.previous_documents;
  const documentsToRemove = individualData.documents_to_remove;
  // eslint-disable-next-line no-param-reassign
  delete individualData.documents;
  // eslint-disable-next-line no-param-reassign
  delete individualData.documents_to_remove;
  // eslint-disable-next-line no-param-reassign
  delete individualData.previous_documents;
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
  const documentsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>ID Type</TableCell>
        <TableCell align='left'>Country</TableCell>
        <TableCell align='left'>Number</TableCell>
      </TableRow>
    </TableHead>
  );
  return (
    <div>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>Type of Data</TableCell>
            <TableCell align='left'>
              {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
                ? 'Previous'
                : 'Current'}{' '}
              Value
            </TableCell>
            <TableCell align='left'>New Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {entries.map((row, index) => {
            const fieldName = camelCase(row[0]);
            const isItemSelected = isSelected(fieldName);
            const labelId = `enhanced-table-checkbox-${index}`;
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              previousValue: string;
              approveStatus: boolean;
            };
            const currentValue =
              ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
                ? valueDetails.previousValue
                : ticket.individualDataUpdateTicketDetails.individual[
                    fieldName
                  ];
            const field = fieldsDict[row[0]];
            return (
              <TableRow
                role='checkbox'
                aria-checked={isItemSelected}
                key={fieldName}
              >
                <TableCell>
                  {isEdit ? (
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
                  ) : (
                    isItemSelected && (
                      <GreenIcon>
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
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
      {documents.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>Documents to be added</Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {documentsTableHead}
            <TableBody>
              {documents?.map((row, index) => {
                return (
                  <TableRow>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          color='primary'
                          onChange={(event) => {
                            handleSelectDocument(index, event.target.checked);
                          }}
                          disabled={
                            ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                          }
                          checked={selectedDocuments.includes(index)}
                          inputProps={{ 'aria-labelledby': 'selected' }}
                        />
                      ) : (
                        selectedDocuments.includes(index) && (
                          <GreenIcon>
                            <CheckCircleIcon />
                          </GreenIcon>
                        )
                      )}
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
            </TableBody>
          </Table>
        </>
      ) : null}
      {documentsToRemove.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>Documents to be removed</Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {documentsTableHead}
            <TableBody>
              {documentsToRemove?.map((row, index) => {
                const document = previousDocuments[row.value];
                return (
                  <TableRow>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          onChange={(event) => {
                            handleSelectDocumentToRemove(
                              index,
                              event.target.checked,
                            );
                          }}
                          color='primary'
                          disabled={
                            ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                          }
                          checked={selectedDocumentsToRemove.includes(index)}
                          inputProps={{ 'aria-labelledby': 'xd' }}
                        />
                      ) : (
                        selectedDocumentsToRemove.includes(index) && (
                          <GreenIcon>
                            <CheckCircleIcon />
                          </GreenIcon>
                        )
                      )}
                    </TableCell>
                    <TableCell align='left'>{document?.label || '-'}</TableCell>
                    <TableCell align='left'>
                      {countriesDict[document?.country] || '-'}
                    </TableCell>
                    <TableCell align='left'>
                      {document?.document_number || '-'}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </>
      ) : null}
    </div>
  );
}
