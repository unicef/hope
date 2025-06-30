import { Checkbox, TableCell, TableRow } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import styled from 'styled-components';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { CurrentValue } from './CurrentValue';
import { NewValue } from './NewValue';
import { ReactElement } from 'react';
import { snakeCase } from 'lodash';

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
  countriesDict,
  isEdit,
  handleSelectBioData,
): ReactElement => {
  const fieldName = camelCase(row[0]);
  const isItemSelected = isSelected(row[0]);
  const labelId = `enhanced-table-checkbox-${index}`;
  const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
    value: string;
    previousValue: string;
    approveStatus: boolean;
  };
  const field = fieldsDict[snakeCase(row[0])];

  const isCountryFieldName =
    fieldName === 'country' ||
    fieldName === 'country_origin' ||
    fieldName === 'countryOrigin';

  const previousValue = isCountryFieldName
    ? countriesDict[valueDetails.previousValue]
    : valueDetails.previousValue;

  const individualValue = field?.isFlexField
    ? ticket.ticketDetails?.individual?.flexFields[row[0]]
    : isCountryFieldName
      ? countriesDict[ticket.ticketDetails?.individual[camelCase(fieldName)]]
      : ticket.ticketDetails?.individual[camelCase(fieldName)];

  const currentValue =
    ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
      ? previousValue
      : individualValue;

  const newValue = isCountryFieldName
    ? countriesDict[valueDetails.value]
    : valueDetails.value;

  return (
    <TableRow role="checkbox" aria-checked={isItemSelected} key={fieldName}>
      <TableCell>
        {isEdit ? (
          <Checkbox
            onChange={(event) =>
              handleSelectBioData(row[0], event.target.checked)
            }
            color="primary"
            disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
            checked={isItemSelected}
            inputProps={{ 'aria-labelledby': labelId }}
            data-cy="checkbox-requested-data-change"
          />
        ) : (
          isItemSelected && (
            <GreenIcon data-cy="green-tick">
              <CheckCircleIcon />
            </GreenIcon>
          )
        )}
      </TableCell>
      <TableCell id={labelId} scope="row" align="left">
        <Capitalize>
          {row[0] === 'sex'
            ? 'gender'
            : row[0].replaceAll('_i_f', '').replaceAll('_', ' ')}
        </Capitalize>
      </TableCell>
      <TableCell align="left" data-cy="current-value">
        <CurrentValue field={field} value={currentValue} />
      </TableCell>
      <TableCell align="left" data-cy="new-value">
        <NewValue field={field} value={newValue} />
      </TableCell>
    </TableRow>
  );
};
