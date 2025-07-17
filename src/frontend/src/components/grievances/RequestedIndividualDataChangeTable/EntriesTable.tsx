import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import camelCase from 'lodash/camelCase';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { handleSelected } from '../utils/helpers';
import { individualDataRow } from './individualDataRow';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

const StyledTable = styled(Table)`
  min-width: 100px;
  width: 100%;
`;

export interface EntriesTableProps {
  values;
  isEdit;
  fieldsDict;
  countriesDict;
  ticket: GrievanceTicketDetail;
  entries;
  entriesFlexFields;
  setFieldValue;
  individual: IndividualDetail;
}

export function EntriesTable({
  values,
  isEdit,
  fieldsDict,
  countriesDict,
  ticket,
  entries,
  entriesFlexFields,
  setFieldValue,
  individual,
}: EntriesTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedFlexFields } = values;
  const selectedBioData = values.selected;
  const isSelected = (name: string): boolean =>
    selectedBioData.includes(camelCase(name));
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);
  const handleSelectBioData = (name): void => {
    handleSelected(camelCase(name), 'selected', selectedBioData, setFieldValue);
  };
  const handleFlexFields = (name): void => {
    handleSelected(
      name,
      'selectedFlexFields',
      selectedFlexFields,
      setFieldValue,
    );
  };

  return (
    <StyledTable>
      <TableHead>
        <TableRow>
          <TableCell align="left" />
          <TableCell data-cy="table-cell-type-of-data" align="left">
            {t('Type of Data')}
          </TableCell>
          <TableCell data-cy="table-cell-previous-current-value" align="left">
            {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
              ? t('Previous')
              : t('Current')}{' '}
            {t('Value')}
          </TableCell>
          <TableCell data-cy="table-cell-new-value" align="left">
            {t('New Value')}
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {entries?.map((row, index) =>
          individualDataRow(
            row,
            isSelected,
            index,
            ticket,
            fieldsDict,
            countriesDict,
            isEdit,
            handleSelectBioData,
            individual,
          ),
        )}
        {entriesFlexFields?.map((row, index) =>
          individualDataRow(
            row,
            isSelectedFlexfields,
            index,
            ticket,
            fieldsDict,
            countriesDict,
            isEdit,
            handleFlexFields,
            individual,
          ),
        )}
      </TableBody>
    </StyledTable>
  );
}
