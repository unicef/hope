import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import { HeadOfHousehold } from '@restgenerated/models/HeadOfHousehold';
import { Recipient } from '@restgenerated/models/Recipient';
import { householdStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface RecipientsTableRowProps {
  household: Recipient;
  headOfHousehold: HeadOfHousehold;
  canViewDetails: boolean;
}

export const RecipientsTableRow = ({
  household,
  headOfHousehold,
  canViewDetails,
}: RecipientsTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();

  const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
  const handleClick = (): void => {
    navigate(householdDetailsPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={household.unicefId}
    >
      <TableCell align="left">
        <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{headOfHousehold.fullName}</AnonTableCell>
      <TableCell align="left">{household.size}</TableCell>
      <TableCell align="left">{household.admin2?.name || '-'}</TableCell>
      <TableCell align="left">{household.residenceStatus}</TableCell>
      <TableCell align="right">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
