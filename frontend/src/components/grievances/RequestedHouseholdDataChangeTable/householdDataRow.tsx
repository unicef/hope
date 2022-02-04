import { Checkbox, TableCell, TableRow } from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import React from 'react';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { CurrentValue } from './CurrentValue';
import { NewValue } from './NewValue';

const GreenIcon = styled.div`
  color: #28cb15;
`;
const Capitalize = styled.span`
  text-transform: capitalize;
`;

export const householdDataRow = (
  row,
  fieldsDict,
  isSelected,
  index,
  countriesDict,
  ticket,
  isEdit,
  handleSelectBioData,
): React.ReactElement => {
  const fieldName = row[0];
  const field = fieldsDict[row[0]];
  const isItemSelected = isSelected(fieldName);
  const labelId = `enhanced-table-checkbox-${index}`;
  const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
    value: string;
    previousValue: string;
    approveStatus: boolean;
  };
  const previousValue =
    fieldName === 'country' || fieldName === 'countryOrigin'
      ? countriesDict[valueDetails.previousValue]
      : valueDetails.previousValue;
  const householdValue = field.isFlexField
    ? ticket.householdDataUpdateTicketDetails.household.flexFields[fieldName]
    : ticket.householdDataUpdateTicketDetails.household[camelCase(fieldName)];
  const currentValue =
    ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
      ? previousValue
      : householdValue;
  return (
    <TableRow role='checkbox' aria-checked={isItemSelected} key={fieldName}>
      <TableCell>
        {isEdit ? (
          <Checkbox
            onChange={(event) =>
              handleSelectBioData(fieldName, event.target.checked)
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
          {row[0].replaceAll('_h_f', '').replaceAll('_', ' ')}
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
};
