import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import moment from 'moment';
import styled from 'styled-components';
import {
  HouseholdChoiceDataQuery,
  ImportedIndividualMinimalFragment,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  choicesToDict,
  decodeIdString,
  sexToCapitalize,
} from '../../../../utils/utils';
import { MiśTheme } from '../../../../theme';
import { TableRow } from '@material-ui/core';

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
  const deduplicationBatchDict = choicesToDict(
    choices.deduplicationBatchStatusChoices,
  );
  const deduplicationGoldenRecordDict = choicesToDict(
    choices.deduplicationGoldenRecordStatusChoices,
  );

  const Error = styled.span`
    color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
    text-decoration: underline;
    cursor: pointer;
  `;
  const Pointer = styled.span`
    cursor: pointer;
  `;
  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/individual/${individual.id}`;
    history.push(path);
  };
  if (individual.deduplicationBatchResults.length) {
    console.log(individual.deduplicationBatchResults);
  }
  return (
    <TableRow hover key={individual.id}>
      <TableCell onClick={handleClick} align='left'>
        <Pointer>{decodeIdString(individual.id)}</Pointer>
      </TableCell>
      <TableCell align='left'>{individual.fullName}</TableCell>
      <TableCell align='left'>{roleChoicesDict[individual.role]}</TableCell>
      <TableCell align='left'>
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align='left'>
        {moment(individual.birthDate).format('DD MMM YYYY')}
      </TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell onClick={() => console.log('click first')} align='left'>
        {individual.deduplicationBatchResults.length ? (
          <Error>
            {deduplicationBatchDict[individual.deduplicationBatchStatus]} (
            {individual.deduplicationBatchResults.length})
          </Error>
        ) : (
          `${deduplicationBatchDict[individual.deduplicationBatchStatus]}`
        )}
      </TableCell>
      <TableCell onClick={() => console.log('click second')} align='left'>
        {individual.deduplicationGoldenRecordResults.length ? (
          <Error>
            {
              deduplicationGoldenRecordDict[
                individual.deduplicationGoldenRecordStatus
              ]
            }{' '}
            ({individual.deduplicationGoldenRecordResults.length})
          </Error>
        ) : (
          `${
            deduplicationGoldenRecordDict[
              individual.deduplicationGoldenRecordStatus
            ]
          }`
        )}
      </TableCell>
    </TableRow>
  );
}
