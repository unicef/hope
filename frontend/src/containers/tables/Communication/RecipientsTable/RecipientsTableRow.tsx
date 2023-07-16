import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../components/core/BlackLink';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { StatusBox } from '../../../../components/core/StatusBox';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { choicesToDict, householdStatusToColor } from '../../../../utils/utils';
import {
  HouseholdNode,
  IndividualNode,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';

interface RecipientsTableRowProps {
  household: HouseholdNode;
  headOfHousehold: IndividualNode;
  canViewDetails: boolean;
}

export function RecipientsTableRow({
  household,
  headOfHousehold,
  canViewDetails,
}: RecipientsTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-first',
  });
  const residenceStatusChoiceDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    history.push(householdDetailsPath);
  };
  if (choicesLoading) return <LoadingComponent />;
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.unicefId}
    >
      <TableCell align='left'>
        <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{headOfHousehold.fullName}</AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.admin2?.name || '-'}</TableCell>
      <TableCell align='left'>
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
