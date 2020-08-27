import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import moment from 'moment';
import {
  HouseholdChoiceDataQuery,
  ImportedIndividualMinimalFragment,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { choicesToDict, decodeIdString } from '../../../../utils/utils';

interface ImportedIndividualsTableRowProps {
  individual: ImportedIndividualMinimalFragment;
  choices: HouseholdChoiceDataQuery;
}

export function ImportedIndividualsTableRow({
  individual,
  choices,
}: ImportedIndividualsTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const relationshipChoicesDict = choicesToDict(choices.relationshipChoices);
  const roleChoicesDict = choicesToDict(choices.roleChoices);
  const batchStatusChoicesDict = choicesToDict(choices.deduplicationBatchStatusChoices);
  const goldenRecordStatusChoicesDict = choicesToDict(choices.deduplicationGoldenRecordStatusChoices);
  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/individual/${individual.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow hover onClick={handleClick} key={individual.id}>
      <TableCell align='left'>{decodeIdString(individual.id)}</TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>{roleChoicesDict[individual.role]}</TableCell>
      <TableCell align='left'>
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align='left'>
        {moment(individual.birthDate).format('DD MMM YYYY')}
      </TableCell>
      <TableCell align='left'>{individual.sex}</TableCell>
      <TableCell align='left'>{batchStatusChoicesDict[individual.deduplicationBatchStatus]}</TableCell>
      <TableCell align='left'>{goldenRecordStatusChoicesDict[individual.deduplicationGoldenRecordStatus]}</TableCell>
    </ClickableTableRow>
  );
}
