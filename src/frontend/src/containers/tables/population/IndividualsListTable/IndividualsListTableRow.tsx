import { BlackLink } from '@components/core/BlackLink';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { HouseholdChoiceDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { choicesToDict, sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface IndividualsListTableRowProps {
  individual: IndividualList;
  canViewDetails: boolean;
  choicesData: HouseholdChoiceDataQuery;
}

export function IndividualsListTableRow({
  individual,
  canViewDetails,
  choicesData,
}: IndividualsListTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();

  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );

  const individualDetailsPath = `/${baseUrl}/population/individuals/${individual.id}`;
  const handleClick = (): void => {
    navigate(individualDetailsPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={individual.id}
      data-cy="individual-table-row"
    >
      <TableCell align="left">
        <IndividualFlags individual={individual} />
      </TableCell>
      <TableCell align="left">
        <BlackLink to={individualDetailsPath}>{individual.unicefId}</BlackLink>
      </TableCell>
      <AnonTableCell>{individual.fullName}</AnonTableCell>
      <TableCell align="left">
        {individual.household ? individual.household.unicefId : ''}
      </TableCell>
      <TableCell align="left">
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align="right">{individual.age}</TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">{individual.household?.admin2?.name}</TableCell>
    </ClickableTableRow>
  );
}
