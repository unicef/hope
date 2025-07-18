import withErrorBoundary from '@components/core/withErrorBoundary';
import { LoadingComponent } from '@core/LoadingComponent';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { handleSelected } from '../utils/helpers';
import { householdDataRow } from './householdDataRow';
import { snakeCase } from 'lodash';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';

interface RequestedHouseholdDataChangeTableProps {
  ticket: GrievanceTicketDetail;
  setFieldValue;
  isEdit;
  values;
}

export const StyledTable = styled(Table)`
  min-width: 100px;
`;

function RequestedHouseholdDataChangeTable({
  setFieldValue,
  ticket,
  isEdit,
  values,
}: RequestedHouseholdDataChangeTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessAreaSlug } = useBaseUrl();

  const { data: householdFieldsData, isLoading: loading } = useQuery({
    queryKey: ['householdFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });

  const { data: countriesData, isLoading: countriesLoading } = useQuery({
    queryKey: ['countriesList'],
    queryFn: () => RestService.restChoicesCountriesList(),
  });

  const { data: household, isLoading: householdLoading } =
    useHopeDetailsQuery<HouseholdDetail>(
      ticket.household.id,
      RestService.restBusinessAreasProgramsHouseholdsRetrieve,
      {},
    );

  // Convert selectedBioData to snake_case
  const selectedBioData = values.selected.map((name) => snakeCase(name));
  const { selectedFlexFields } = values;
  const householdData = {
    ...ticket.ticketDetails.householdData,
  };
  const flexFields = householdData.flexFields || {};
  delete householdData.flexFields;
  const entriesHouseholdData = Object.entries(householdData);
  const entriesHouseholdDataFlexFields = Object.entries(flexFields);
  //@ts-ignore
  const fieldsDict = useArrayToDict(householdFieldsData, 'name', '*');
  const countriesDict = useArrayToDict(countriesData, 'isoCode2', 'name');

  if (loading || countriesLoading || !fieldsDict || householdLoading) {
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
    handleSelected(snakeCase(name), 'selected', selectedBioData, setFieldValue);
  };
  const roles =
    ticket.householdDataUpdateTicketDetails.householdData.roles || [];

  const isSelected = (name: string): boolean =>
    selectedBioData.includes(snakeCase(name));
  const isSelectedFlexfields = (name: string): boolean =>
    selectedFlexFields.includes(name);

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
