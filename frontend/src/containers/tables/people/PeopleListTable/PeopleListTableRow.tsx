import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  HouseholdChoiceDataQuery,
  IndividualNode,
  IndividualRelationship,
} from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { choicesToDict, sexToCapitalize } from '@utils/utils';

interface IndividualsListTableRowProps {
  individual: IndividualNode;
  canViewDetails: boolean;
  choicesData: HouseholdChoiceDataQuery;
}

export function PeopleListTableRow({
  individual,
  canViewDetails,
  choicesData,
}: IndividualsListTableRowProps): React.ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();

  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );

  const individualDetailsPath = `/${baseUrl}/population/people/${individual.id}`;
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
      <TableCell align="right">
        {individual.relationship === IndividualRelationship.Head
          ? t('Beneficiary')
          : t('Non-beneficiary')}
      </TableCell>
      <TableCell align="right">{individual.age}</TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">{individual.household?.admin2?.name}</TableCell>
    </ClickableTableRow>
  );
}
