import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { choicesToDict, householdStatusToColor } from '@utils/utils';
import { HouseholdNode, IndividualNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

interface RecipientsTableRowProps {
  household: HouseholdNode;
  headOfHousehold: IndividualNode;
  canViewDetails: boolean;
}

export const RecipientsTableRow = ({
  household,
  headOfHousehold,
  canViewDetails,
}: RecipientsTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl, businessArea } = useBaseUrl();

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });
  if (choicesLoading) return <LoadingComponent />;
  if (!choicesData) return null;
  const residenceStatusChoiceDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
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
      <TableCell align="left">
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align="right">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
