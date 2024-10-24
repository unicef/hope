import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { choicesToDict, householdStatusToColor } from '@utils/utils';
import {
  HouseholdNode,
  IndividualNode,
  useHouseholdChoiceDataQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface RecipientsTableRowProps {
  household: HouseholdNode;
  headOfHousehold: IndividualNode;
  canViewDetails: boolean;
}

export const RecipientsTableRow = ({
  household,
  headOfHousehold,
  canViewDetails,
}: RecipientsTableRowProps): React.ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery({
      fetchPolicy: 'cache-first',
    });
  const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
  const handleClick = (): void => {
    navigate(householdDetailsPath);
  };

  if (choicesLoading) return <LoadingComponent />;
  if (!choicesData) return null;

  const residenceStatusChoiceDict = choicesToDict(
    choicesData?.residenceStatusChoices,
  );

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
      <TableCell align="left">
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align="right">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
