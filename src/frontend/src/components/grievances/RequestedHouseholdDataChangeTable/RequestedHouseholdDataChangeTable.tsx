import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Checkbox } from '@mui/material';

const GreenIcon = styled.div`
  color: #28cb15;
`;
import { useArrayToDict } from '@hooks/useArrayToDict';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useAllEditHouseholdFieldsQuery } from '@generated/graphql';
import { handleSelected } from '../utils/helpers';
import { householdDataRow } from './householdDataRow';
import withErrorBoundary from '@components/core/withErrorBoundary';
type RequestedHouseholdDataChangeTableProps = {
  ticket: any;
  setFieldValue: any;
  isEdit: boolean;
  values: any;
};
function RequestedHouseholdDataChangeTable(
  props: RequestedHouseholdDataChangeTableProps,
): ReactElement {
  const { t } = useTranslation();
  const { data } = useAllEditHouseholdFieldsQuery();
  const { setFieldValue, ticket, isEdit, values } = props;
  const selectedBioData = values.selected;
  const { selectedFlexFields } = values;
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  const isSelected = (name: string): boolean => selectedBioData.includes(name);
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);
  const selectedRoles = values.selectedRoles || [];
  const handleSelectRole = (individualId: string): void => {
    handleSelected(individualId, 'selectedRoles', selectedRoles, setFieldValue);
  };
  const flexFields = householdData.flex_fields || {};
  delete householdData.flex_fields;
  const entries = Object.entries(householdData).filter(
    ([key]) => key !== 'roles',
  );
  const entriesFlexFields = Object.entries(flexFields);
  const fieldsDict = useArrayToDict(
    data?.allEditHouseholdFieldsAttributes,
    'name',
    '*',
  );

  console.log('entries', entries);
  console.log('entriesFlexFields', entriesFlexFields);
  const countriesDict = useArrayToDict(data?.countriesChoices, 'value', 'name');

  const StyledTable = styled(Table)`
    min-width: 100px;
  `;

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
  const roles =
    ticket.householdDataUpdateTicketDetails.householdData.roles || [];

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
        {entries.length > 0 &&
          entries.map((row, index) =>
            householdDataRow(
              row,
              fieldsDict,
              isSelected,
              index,
              countriesDict,
              ticket,
              isEdit,
              handleSelectBioData,
            ),
          )}
        {roles.length > 0 &&
          roles.map((role, index) => {
            const labelId = `enhanced-table-checkbox-role-${index}`;
            const isRoleSelected = selectedRoles.includes(role.individual_id);
            return (
              <TableRow
                key={`role-row-${role.individual_id}`}
                role="checkbox"
                aria-checked={isRoleSelected}
              >
                <TableCell>
                  {isEdit ? (
                    <Checkbox
                      data-cy="checkbox-household-role"
                      onChange={() => handleSelectRole(role.individual_id)}
                      color="primary"
                      disabled={
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                      checked={isRoleSelected}
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  ) : (
                    isRoleSelected && (
                      <GreenIcon data-cy="green-tick-role">
                        <CheckCircleIcon />
                      </GreenIcon>
                    )
                  )}
                </TableCell>
                <TableCell id={labelId} scope="row" align="left">
                  {`Roles (${role.full_name})`}
                </TableCell>
                <TableCell align="left">{role.previous_value}</TableCell>
                <TableCell align="left">{role.value}</TableCell>
              </TableRow>
            );
          })}
        {entriesFlexFields.length > 0 &&
          entriesFlexFields.map((row, index) =>
            householdDataRow(
              row,
              fieldsDict,
              isSelectedFlexfields,
              index,
              countriesDict,
              ticket,
              isEdit,
              handleFlexFields,
            ),
          )}
      </TableBody>
    </StyledTable>
  );
}
export default withErrorBoundary(
  RequestedHouseholdDataChangeTable,
  'RequestedHouseholdDataChangeTable',
);
