import React from 'react';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import styled from 'styled-components';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import { Checkbox, TableCell, TableRow } from '@material-ui/core';
import { CurrentValue } from './CurrentValue';
import { NewValue } from './NewValue';

const GreenIcon = styled.div`
  color: #28cb15;
`;

const Capitalize = styled.span`
  text-transform: capitalize;
`;

export const individualDataRow = (
  row,
  isSelected,
  index,
  ticket,
  fieldsDict,
  isEdit,
  handleSelectBioData,
): React.ReactElement => {
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
};
