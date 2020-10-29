import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { TableRow } from '@material-ui/core';
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
import { DedupeResults } from '../../details/DedupeResults';
import { UniversalMoment } from '../../../../components/UniversalMoment';
import { Pointer } from '../../../../components/Pointer';

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

  const handleClick = (): void => {
    const path = `/${businessArea}/registration-data-import/individual/${individual.id}`;
    history.push(path);
  };
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
        <UniversalMoment>{individual.birthDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align='left'>
        {individual.deduplicationBatchResults.length ? (
          <>
            <DedupeResults
              isInBatch
              status={
                deduplicationBatchDict[individual.deduplicationBatchStatus]
              }
              results={individual.deduplicationBatchResults}
              individual={individual}
            />
          </>
        ) : (
          `${deduplicationBatchDict[individual.deduplicationBatchStatus]}`
        )}
      </TableCell>
      <TableCell align='left'>
        {individual.deduplicationGoldenRecordResults.length ? (
          <DedupeResults
            status={
              deduplicationGoldenRecordDict[
                individual.deduplicationGoldenRecordStatus
              ]
            }
            results={individual.deduplicationGoldenRecordResults}
            individual={individual}
          />
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
