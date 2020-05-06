import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../utils/utils';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
}

export function TargetPopulationHouseholdTableRow({ household }) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    const win = window.open(path, '_blank');
    if (win != null) {
      win.focus();
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{decodeIdString(household.id)}</TableCell>
      <TableCell align='left'>{`${household.headOfHousehold.givenName} ${household.headOfHousehold.familyName}`}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.address}</TableCell>
      <TableCell align='left'>{household.adminArea.title}</TableCell>
    </ClickableTableRow>
  );
}
