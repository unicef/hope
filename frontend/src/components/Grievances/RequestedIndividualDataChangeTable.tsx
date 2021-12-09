import { Box, Checkbox, makeStyles, Typography } from '@material-ui/core';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useArrayToDict } from '../../hooks/useArrayToDict';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  AllAddIndividualFieldsQuery,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { PhotoModal } from '../PhotoModal/PhotoModal';
import { GrievanceFlexFieldPhotoModal } from './GrievanceFlexFieldPhotoModal';

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
const GreyText = styled.div`
  color: #9e9e9e;
`;
export interface CurrentValueProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  value;
}

export function CurrentValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue;
  switch (field?.type) {
    case 'SELECT_ONE':
      displayValue =
        field.choices.find((item) => item.value === value)?.labelEn || '-';
      break;
    case 'SELECT_MANY':
      displayValue =
        field.choices.find((item) => item.value === value)?.labelEn || '-';
      if (value instanceof Array) {
        displayValue = value
          .map(
            (choice) =>
              field.choices.find((item) => item.value === choice)?.labelEn ||
              '-',
          )
          .join(', ');
      }
      break;
    case 'BOOL':
      /* eslint-disable-next-line no-nested-ternary */
      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    case 'IMAGE':
      displayValue = (
        <GrievanceFlexFieldPhotoModal field={field} isCurrent isIndividual />
      );
      break;
    default:
      displayValue = value;
  }
  return <>{displayValue || '-'}</>;
}

export function NewValue({
  field,
  value,
}: CurrentValueProps): React.ReactElement {
  let displayValue;
  switch (field?.type) {
    case 'SELECT_ONE':
      displayValue =
        field.choices.find((item) => item.value === value)?.labelEn || '-';
      break;
    case 'SELECT_MANY':
      displayValue =
        field.choices.find((item) => item.value === value)?.labelEn || '-';
      if (value instanceof Array) {
        displayValue = value
          .map(
            (choice) =>
              field.choices.find((item) => item.value === choice)?.labelEn ||
              '-',
          )
          .join(', ');
      }
      break;
    case 'BOOL':
      /* eslint-disable-next-line no-nested-ternary */
      displayValue = value === null ? '-' : value ? 'Yes' : 'No';
      break;
    case 'IMAGE':
      displayValue = (
        <GrievanceFlexFieldPhotoModal field={field} isIndividual />
      );
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

function individualDataRow(
  row,
  isSelected,
  index,
  ticket,
  fieldsDict,
  isEdit,
  handleSelectBioData,
): ReactElement {
  const fieldName = camelCase(row[0]);
  const isItemSelected = isSelected(row[0]);
  const labelId = `enhanced-table-checkbox-${index}`;
  const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
    value: string;
    previousValue: string;
    approveStatus: boolean;
  };
  const field = fieldsDict[row[0]];
  const individualValue = field.isFlexField
    ? ticket.individualDataUpdateTicketDetails?.individual?.flexFields[row[0]]
    : ticket.individualDataUpdateTicketDetails?.individual[
        camelCase(fieldName)
      ];
  const currentValue =
    ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
      ? valueDetails.previousValue
      : individualValue;
  return (
    <TableRow role='checkbox' aria-checked={isItemSelected} key={fieldName}>
      <TableCell>
        {isEdit ? (
          <Checkbox
            onChange={(event) =>
              handleSelectBioData(row[0], event.target.checked)
            }
            color='primary'
            disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
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
        <Capitalize>
          {row[0] === 'sex'
            ? 'gender'
            : row[0].replaceAll('_i_f', '').replaceAll('_', ' ')}
        </Capitalize>
      </TableCell>
      <TableCell align='left'>
        <CurrentValue field={field} value={currentValue} />
      </TableCell>
      <TableCell align='left'>
        <NewValue field={field} value={valueDetails.value} />
      </TableCell>
    </TableRow>
  );
}

export function RequestedIndividualDataChangeTable({
  setFieldValue,
  ticket,
  values,
  isEdit,
}: RequestedIndividualDataChangeTableProps): ReactElement {
  const { t } = useTranslation();
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();

  const selectedBioData = values.selected;
  const { selectedDocuments } = values;
  const { selectedDocumentsToRemove } = values;
  const { selectedDocumentsToEdit } = values;
  const { selectedFlexFields } = values;
  const { selectedIdentities } = values;
  const { selectedIdentitiesToEdit } = values;
  const { selectedIdentitiesToRemove } = values;
  const { data, loading } = useAllAddIndividualFieldsQuery();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const documents = individualData?.documents;
  const previousDocuments = individualData.previous_documents;
  const documentsToRemove = individualData.documents_to_remove;
  const documentsToEdit = individualData.documents_to_edit;
  const identities = individualData?.identities;
  const previousIdentities = individualData.previous_identities;
  const identitiesToRemove = individualData.identities_to_remove;
  const identitiesToEdit = individualData.identities_to_edit;
  const flexFields = individualData.flex_fields;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;
  delete individualData.documents_to_edit;
  delete individualData.identities;
  delete individualData.identities_to_remove;
  delete individualData.identities_to_edit;
  delete individualData.previous_identities;
  delete individualData.flex_fields;
  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
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
  const identityTypeDict = useArrayToDict(
    data?.identityTypeChoices,
    'value',
    'name',
  );

  if (
    loading ||
    !fieldsDict ||
    !countriesDict ||
    !documentTypeDict ||
    !identityTypeDict
  ) {
    return <LoadingComponent />;
  }

  const handleSelectBioData = (name): void => {
    const newSelected = [...selectedBioData];
    const selectedIndex = newSelected.indexOf(camelCase(name));
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(camelCase(name));
    }
    setFieldValue('selected', newSelected);
  };
  const handleFlexFields = (name): void => {
    const newSelected = [...selectedFlexFields];
    const selectedIndex = newSelected.indexOf(name);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(name);
    }
    setFieldValue('selectedFlexFields', newSelected);
  };
  const handleSelectDocument = (documentIndex): void => {
    const newSelected = [...selectedDocuments];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocuments', newSelected);
  };
  const handleSelectDocumentToEdit = (documentIndex): void => {
    const newSelected = [...selectedDocumentsToEdit];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocumentsToEdit', newSelected);
  };

  const handleSelectIdentity = (identityIndex): void => {
    const newSelected = [...selectedIdentities];
    const selectedIndex = newSelected.indexOf(identityIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(identityIndex);
    }
    setFieldValue('selectedIdentities', newSelected);
  };

  const handleSelectIdentityToEdit = (documentIndex): void => {
    const newSelected = [...selectedIdentitiesToEdit];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedIdentitiesToEdit', newSelected);
  };

  const handleSelectDocumentToRemove = (documentIndex): void => {
    const newSelected = [...selectedDocumentsToRemove];
    const selectedIndex = newSelected.indexOf(documentIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(documentIndex);
    }
    setFieldValue('selectedDocumentsToRemove', newSelected);
  };
  const handleSelectIdentityToRemove = (identityIndex): void => {
    const newSelected = [...selectedIdentitiesToRemove];
    const selectedIndex = newSelected.indexOf(identityIndex);
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(identityIndex);
    }
    setFieldValue('selectedIdentitiesToRemove', newSelected);
  };

  const isSelected = (name: string): boolean =>
    selectedBioData.includes(camelCase(name));
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);
  const documentsTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>{t('ID Type')}</TableCell>
        <TableCell align='left'>{t('Country')}</TableCell>
        <TableCell align='left'>{t('Number')}</TableCell>
      </TableRow>
    </TableHead>
  );
  const identitiesTableHead = (
    <TableHead>
      <TableRow>
        <TableCell align='left' />
        <TableCell align='left'>{t('Agency')}</TableCell>
        <TableCell align='left'>{t('Country')}</TableCell>
        <TableCell align='left'>{t('Number')}</TableCell>
      </TableRow>
    </TableHead>
  );

  const renderCurrentPhoto = (document): React.ReactElement => {
    if (document.value?.photo === document.previous_value?.photo) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    if (!document.value?.photo) {
      return <span>-</span>;
    }
    return <PhotoModal src={document.value.photo} />;
  };

  const renderNewOrNotUpdated = (prev, curr): React.ReactElement => {
    if (prev === curr) {
      return <GreyText>{t('Not updated')}</GreyText>;
    }
    return <span>{curr}</span>;
  };

  return (
    <div>
      {entries?.length ? (
        <Table className={classes.table}>
          <TableHead>
            <TableRow>
              <TableCell align='left' />
              <TableCell align='left'>{t('Type of Data')}</TableCell>
              <TableCell align='left'>
                {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
                  ? t('Previous')
                  : t('Current')}
                {t('Value')}
              </TableCell>
              <TableCell align='left'>{t('New Value')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((row, index) => {
              return individualDataRow(
                row,
                isSelected,
                index,
                ticket,
                fieldsDict,
                isEdit,
                handleSelectBioData,
              );
            })}
            {entriesFlexFields.map((row, index) => {
              return individualDataRow(
                row,
                isSelectedFlexfields,
                index,
                ticket,
                fieldsDict,
                isEdit,
                handleFlexFields,
              );
            })}
          </TableBody>
        </Table>
      ) : null}
      {documents?.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>{t('Documents to be added')}</Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {documentsTableHead}
            <TableBody>
              {documents?.map((row, index) => {
                return (
                  <TableRow key={`${row.value.type}-${row.value.country}`}>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          color='primary'
                          onChange={(): void => {
                            handleSelectDocument(index);
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
      {documentsToEdit?.length
        ? documentsToEdit.map((document, index) => (
            <div key={document.previous_value.number}>
              <Title>
                <Box display='flex' justifyContent='space-between'>
                  <Typography variant='h6'>
                    {t('Document to be edited')}
                  </Typography>
                </Box>
              </Title>
              <Table className={classes.table}>
                <TableHead>
                  <TableRow>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          color='primary'
                          onChange={(): void => {
                            handleSelectDocumentToEdit(index);
                          }}
                          disabled={
                            ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                          }
                          checked={selectedDocumentsToEdit.includes(index)}
                          inputProps={{ 'aria-labelledby': 'selected' }}
                        />
                      ) : (
                        selectedDocumentsToEdit.includes(index) && (
                          <GreenIcon>
                            <CheckCircleIcon />
                          </GreenIcon>
                        )
                      )}
                    </TableCell>
                    <TableCell align='left'>{t('Field')}</TableCell>
                    <TableCell align='left'>{t('Current Value')}</TableCell>
                    <TableCell align='left'>{t('New Value')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell />
                    <TableCell align='left'>{t('Country')}</TableCell>
                    <TableCell align='left'>
                      {countriesDict[document.previous_value.country]}
                    </TableCell>
                    <TableCell align='left'>
                      {renderNewOrNotUpdated(
                        countriesDict[document.previous_value.country],
                        countriesDict[document.value?.country],
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell />
                    <TableCell align='left'>{t('Document Type')}</TableCell>
                    <TableCell align='left'>
                      {documentTypeDict[document.previous_value.type]}
                    </TableCell>
                    <TableCell align='left'>
                      {renderNewOrNotUpdated(
                        documentTypeDict[document.previous_value.type],
                        documentTypeDict[document.value.type],
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell />

                    <TableCell align='left'>{t('Document Number')}</TableCell>
                    <TableCell align='left'>
                      {document.previous_value.number}
                    </TableCell>
                    <TableCell align='left'>
                      {renderNewOrNotUpdated(
                        documentTypeDict[document.previous_value.number],
                        documentTypeDict[document.value.number],
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell />
                    <TableCell align='left'>{t('Photo')}</TableCell>
                    <TableCell align='left'>
                      {document.previous_value?.photo ? (
                        <PhotoModal src={document.previous_value.photo} />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell align='left'>
                      {renderCurrentPhoto(document)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          ))
        : null}
      {identities?.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>
                {t('Identities to be added')}
              </Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {identitiesTableHead}
            <TableBody>
              {identities?.map((row, index) => {
                return (
                  <TableRow key={`${row.value.agency}-${row.value.agency}`}>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          color='primary'
                          onChange={(): void => {
                            handleSelectIdentity(index);
                          }}
                          disabled={
                            ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                          }
                          checked={selectedIdentities.includes(index)}
                          inputProps={{ 'aria-labelledby': 'selected' }}
                        />
                      ) : (
                        selectedIdentities.includes(index) && (
                          <GreenIcon>
                            <CheckCircleIcon />
                          </GreenIcon>
                        )
                      )}
                    </TableCell>
                    <TableCell align='left'>
                      {identityTypeDict[row.value.agency]}
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
      {identitiesToEdit?.length
        ? identitiesToEdit.map((identity, index) => {
            return (
              <>
                <Title>
                  <Box display='flex' justifyContent='space-between'>
                    <Typography variant='h6'>
                      {t('Identity to be edited')}
                    </Typography>
                  </Box>
                </Title>
                <Table className={classes.table}>
                  <TableHead>
                    <TableRow>
                      <TableCell align='left'>
                        {isEdit ? (
                          <Checkbox
                            color='primary'
                            onChange={(): void => {
                              handleSelectIdentityToEdit(index);
                            }}
                            disabled={
                              ticket.status !==
                              GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                            }
                            checked={selectedIdentitiesToEdit.includes(index)}
                            inputProps={{ 'aria-labelledby': 'selected' }}
                          />
                        ) : (
                          selectedIdentitiesToEdit.includes(index) && (
                            <GreenIcon>
                              <CheckCircleIcon />
                            </GreenIcon>
                          )
                        )}
                      </TableCell>
                      <TableCell align='left'>{t('Field')}</TableCell>
                      <TableCell align='left'>{t('Current Value')}</TableCell>
                      <TableCell align='left'>{t('New Value')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell />
                      <TableCell align='left'>{t('Agency')}</TableCell>
                      <TableCell align='left'>
                        {identity.previous_value.agency}
                      </TableCell>
                      <TableCell align='left'>
                        {identity.value?.agency ?? (
                          <GreyText>{t('Not updated')}</GreyText>
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell />
                      <TableCell align='left'>{t('Country')}</TableCell>
                      <TableCell align='left'>
                        {countriesDict[identity.previous_value.country]}
                      </TableCell>
                      <TableCell align='left'>
                        {renderNewOrNotUpdated(
                          countriesDict[identity.previous_value.country],
                          countriesDict[identity.value?.country],
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell />
                      <TableCell align='left'>{t('Identity Number')}</TableCell>
                      <TableCell align='left'>
                        {identity.previous_value.number}
                      </TableCell>
                      <TableCell align='left'>
                        {renderNewOrNotUpdated(
                          identity.previous_value.number,
                          identity.value?.number,
                        )}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </>
            );
          })
        : null}
      {documentsToRemove?.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>
                {t('Documents to be removed')}
              </Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {documentsTableHead}
            <TableBody>
              {documentsToRemove?.map((row, index) => {
                const document = previousDocuments[row.value];
                return (
                  <TableRow key={`${document.label}-${document.country}`}>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          onChange={(): void => {
                            handleSelectDocumentToRemove(index);
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
      {identitiesToRemove?.length ? (
        <>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>
                {t('Identities to be removed')}
              </Typography>
            </Box>
          </Title>
          <Table className={classes.table}>
            {identitiesTableHead}
            <TableBody>
              {identitiesToRemove?.map((row, index) => {
                const identity = previousIdentities[row.value];
                return (
                  <TableRow key={`${identity.label}-${identity.country}`}>
                    <TableCell align='left'>
                      {isEdit ? (
                        <Checkbox
                          onChange={(): void => {
                            handleSelectIdentityToRemove(index);
                          }}
                          color='primary'
                          disabled={
                            ticket.status !==
                            GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                          }
                          checked={selectedIdentitiesToRemove.includes(index)}
                          inputProps={{ 'aria-labelledby': 'xd' }}
                        />
                      ) : (
                        selectedIdentitiesToRemove.includes(index) && (
                          <GreenIcon>
                            <CheckCircleIcon />
                          </GreenIcon>
                        )
                      )}
                    </TableCell>
                    <TableCell align='left'>{identity?.label || '-'}</TableCell>
                    <TableCell align='left'>
                      {countriesDict[identity?.country] || '-'}
                    </TableCell>
                    <TableCell align='left'>
                      {identity?.number || '-'}
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
