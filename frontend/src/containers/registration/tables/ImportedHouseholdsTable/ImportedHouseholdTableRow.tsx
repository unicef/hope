import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import {
  ImportedHouseholdMinimalFragment,
  ImportedHouseholdNode,
  RegistrationDataImportNode,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../../components/StatusBox';
import {
  decodeIdString,
  registrationDataImportStatusToColor,
} from '../../../../utils/utils';
import moment from 'moment';

const StatusContainer = styled.div`
  width: 120px;
`;

interface PaymentRecordTableRowProps {
  household: ImportedHouseholdMinimalFragment;
}

export function ImportedHouseholdTableRow({
  household,
}: PaymentRecordTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/household/${household.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{decodeIdString(household.id)}</TableCell>
      <TableCell align='left'>
        {household.headOfHousehold && household.headOfHousehold.fullName}
      </TableCell>
      <TableCell align='right'>{household.familySize}</TableCell>
      <TableCell align='left'>{household.location}</TableCell>
      <TableCell align='left'>
        {moment(household.registrationDate).format('DD MMM YYYY')}
      </TableCell>
    </ClickableTableRow>
  );
}
