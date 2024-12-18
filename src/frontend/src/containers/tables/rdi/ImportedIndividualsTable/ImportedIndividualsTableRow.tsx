import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { HouseholdChoiceDataQuery } from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { DedupeResults } from '@components/rdi/details/DedupeResults';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { choicesToDict, sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';

interface ImportedIndividualsTableRowProps {
  individual;
  choices: HouseholdChoiceDataQuery;
  isMerged: boolean;
  rdi;
}

export function ImportedIndividualsTableRow({
  individual,
  choices,
  rdi,
}: ImportedIndividualsTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl, businessArea } = useBaseUrl();

  const relationshipChoicesDict = choicesToDict(choices.relationshipChoices);
  const roleChoicesDict = choicesToDict(choices.roleChoices);
  const deduplicationBatchDict = choicesToDict(
    choices.deduplicationBatchStatusChoices,
  );
  const deduplicationGoldenRecordDict = choicesToDict(
    choices.deduplicationGoldenRecordStatusChoices,
  );

  const individualDetailsPath = `/${baseUrl}/population/individuals/${individual.id}`;

  const handleClick = (): void => {
    navigate(individualDetailsPath, {
      state: {
        breadcrumbTitle: `Registration Data Import: ${rdi.name}`,
        breadcrumbUrl: `/${businessArea}/registration-data-import/${rdi.id}`,
      },
    });
  };

  return (
    <ClickableTableRow
      hover
      onClick={() => handleClick()}
      role="checkbox"
      key={individual.id}
      data-cy="imported-individuals-row"
    >
      <TableCell align="left">
        <BlackLink to={individualDetailsPath}>
          {individual.unicefId}
        </BlackLink>
      </TableCell>
      <AnonTableCell>{individual.fullName}</AnonTableCell>
      <TableCell align="left">{roleChoicesDict[individual.role]}</TableCell>
      <TableCell align="left">
        {relationshipChoicesDict[individual.relationship]}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{individual.birthDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{sexToCapitalize(individual.sex)}</TableCell>
      <TableCell align="left">
        {individual.deduplicationBatchResults?.length ? (
          <DedupeResults
            isInBatch
            status={deduplicationBatchDict[individual.deduplicationBatchStatus]}
            results={individual.deduplicationBatchResults}
            individual={individual}
          />
        ) : (
          `${deduplicationBatchDict[individual.deduplicationBatchStatus]}`
        )}
      </TableCell>
      <TableCell align="left">
        {individual.deduplicationGoldenRecordResults?.length ? (
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
    </ClickableTableRow>
  );
}
