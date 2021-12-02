import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import camelCase from 'lodash/camelCase';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { individualDataRow } from './individualDataRow';

const StyledTable = styled(Table)`
  min-width: 100px;
`;

export interface EntriesTableProps {
  values;
  isEdit;
  fieldsDict;
  ticket: GrievanceTicketQuery['grievanceTicket'];
  entries;
  entriesFlexFields;
  setFieldValue;
}

export const EntriesTable = ({
  values,
  isEdit,
  fieldsDict,
  ticket,
  entries,
  entriesFlexFields,
  setFieldValue,
}: EntriesTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedFlexFields } = values;
  const selectedBioData = values.selected;
  const isSelected = (name: string): boolean =>
    selectedBioData.includes(camelCase(name));
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);
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

  return (
    <StyledTable>
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
    </StyledTable>
  );
};
