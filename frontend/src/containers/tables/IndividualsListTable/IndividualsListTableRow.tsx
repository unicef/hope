import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import {
  IndividualNode,
  useHouseholdChoiceDataQuery,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { Flag } from '../../../components/Flag';
import {
  choicesToDict,
  sexToCapitalize,
} from '../../../utils/utils';
import { FlagTooltip } from '../../../components/FlagTooltip';
import { LoadingComponent } from '../../../components/LoadingComponent';
import { AnonTableCell } from '../../../components/table/AnonTableCell';

interface IndividualsListTableRowProps {
  individual: IndividualNode;
  canViewDetails: boolean;
}

export function IndividualsListTableRow({
  individual,
  canViewDetails,
}: IndividualsListTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (choicesLoading) {
    return <LoadingComponent />;
  }
  const relationshipChoicesDict = choicesToDict(
    choicesData.relationshipChoices,
  );

  const handleClick = (): void => {
    const path = `/${businessArea}/population/individuals/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={individual.id}
    >
      <TableCell align='left'>
        {individual.deduplicationGoldenRecordStatus !== 'UNIQUE' && (
          <FlagTooltip />
        )}
        {(individual.sanctionListPossibleMatch ||
          individual.sanctionListConfirmedMatch) && (
          <Flag confirmed={individual.sanctionListConfirmedMatch} />
        )}
      </TableCell>
      <TableCell align='left'>{individual.unicefId}</TableCell>
      <AnonTableCell>{individual.fullName}</AnonTableCell>
      <TableCell align='left'>
        {individual.household ? individual.household.unicefId : ''}
      </TableCell>
      <TableCell align='left'>
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align='right'>{individual.age}</TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>{individual.household?.admin2?.title}</TableCell>
    </ClickableTableRow>
  );
}
