import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import styled from 'styled-components';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import {
  GrievanceTicketNode,
  useAllEditHouseholdFieldsQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { handleSelected } from '../utils/helpers';
import { householdDataRow } from './householdDataRow';

interface RequestedHouseholdDataChangeTableProps {
  ticket: GrievanceTicketNode;
  setFieldValue;
  isEdit;
  values;
}

export const StyledTable = styled(Table)`
  min-width: 100px;
`;

export function RequestedHouseholdDataChangeTable({
  setFieldValue,
  ticket,
  isEdit,
  values,
}: RequestedHouseholdDataChangeTableProps): ReactElement {
  const { t } = useTranslation();
  const { data, loading } = useAllEditHouseholdFieldsQuery();
  const selectedBioData = values.selected;
  const { selectedFlexFields } = values;
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  const flexFields = householdData.flex_fields || {};
  delete householdData.flex_fields;
  const entries = Object.entries(householdData);
  const entriesFlexFields = Object.entries(flexFields);
  const fieldsDict = useArrayToDict(
    data?.allEditHouseholdFieldsAttributes,
    'name',
    '*',
  );
  const countriesDict = useArrayToDict(data?.countriesChoices, 'value', 'name');
  if (loading || !fieldsDict || !countriesDict) {
    return <LoadingComponent />;
  }

  const handleFlexFields = (name): void => {
    handleSelected(
      name,
      'selectedFlexFields',
      selectedFlexFields,
      setFieldValue,
    );
  };
  const handleSelectBioData = (name): void => {
    handleSelected(name, 'selected', selectedBioData, setFieldValue);
  };

  const isSelected = (name: string): boolean => selectedBioData.includes(name);
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);
  return (
    <StyledTable>
      <TableHead>
        <TableRow>
          <TableCell align='left' />
          <TableCell align='left'>{t('Type of Data')}</TableCell>
          <TableCell align='left'>
            {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
              ? t('Previous')
              : t('Current')}{' '}
            {t('Value')}
          </TableCell>
          <TableCell align='left'>{t('New Value')}</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {entries.map((row, index) => {
          return householdDataRow(
            row,
            fieldsDict,
            isSelected,
            index,
            countriesDict,
            ticket,
            isEdit,
            handleSelectBioData,
          );
        })}
        {entriesFlexFields.map((row, index) => {
          return householdDataRow(
            row,
            fieldsDict,
            isSelectedFlexfields,
            index,
            countriesDict,
            ticket,
            isEdit,
            handleFlexFields,
          );
        })}
      </TableBody>
    </StyledTable>
  );
}
