import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import {
  HouseholdChoiceDataQuery,
  IndividualBiometricDeduplicationBatchStatus,
  IndividualBiometricDeduplicationGoldenRecordStatus,
} from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { choicesToDict, sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';
import { DedupeBiographicalBiometricResults } from '@components/rdi/details/DedupeBiographicalBiometricResults';
import { IndividualList } from '@restgenerated/models/IndividualList';

interface ImportedIndividualsTableRowProps {
  individual: IndividualList;
  choices: HouseholdChoiceDataQuery;
  rdi;
}

export function ImportedPeopleTableRow({
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
  const deduplicationGoldenDict = choicesToDict(
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

  const WORST_STATUS_PRIORITY = [
    IndividualBiometricDeduplicationGoldenRecordStatus.Duplicate,
    IndividualBiometricDeduplicationBatchStatus.DuplicateInBatch,
    IndividualBiometricDeduplicationGoldenRecordStatus.NeedsAdjudication,
    IndividualBiometricDeduplicationBatchStatus.SimilarInBatch,
    IndividualBiometricDeduplicationGoldenRecordStatus.Postpone,
    IndividualBiometricDeduplicationGoldenRecordStatus.Unique,
    IndividualBiometricDeduplicationBatchStatus.UniqueInBatch,
    IndividualBiometricDeduplicationGoldenRecordStatus.NotProcessed,
    IndividualBiometricDeduplicationBatchStatus.NotProcessed,
  ];

  function renderDeduplicationStatus(
    goldenRecordStatus:
      | IndividualBiometricDeduplicationGoldenRecordStatus
      | IndividualBiometricDeduplicationBatchStatus,
    batchStatus:
      | IndividualBiometricDeduplicationGoldenRecordStatus
      | IndividualBiometricDeduplicationBatchStatus,
    dict,
  ): string {
    const statuses = [goldenRecordStatus, batchStatus];
    statuses.sort(
      (a, b) =>
        WORST_STATUS_PRIORITY.indexOf(a) - WORST_STATUS_PRIORITY.indexOf(b),
    );
    return dict[statuses[0]];
  }

  return (
    <ClickableTableRow
      hover
      onClick={() => handleClick()}
      role="checkbox"
      key={individual.id}
      data-cy="imported-individuals-row"
    >
      <TableCell align="left">
        <BlackLink to={individualDetailsPath}>{individual.unicefId}</BlackLink>
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
        {individual.biometricDeduplicationBatchResults?.length ||
        individual.deduplicationBatchResults?.length ? (
          <DedupeBiographicalBiometricResults
            status={renderDeduplicationStatus(
              individual.deduplicationBatchStatus,
              individual.biometricDeduplicationBatchStatus,
              deduplicationBatchDict,
            )}
            results={individual.deduplicationBatchResults}
            biometricResults={individual.biometricDeduplicationBatchResults}
            individual={individual}
            isInBatch
          />
        ) : (
          renderDeduplicationStatus(
            individual.deduplicationBatchStatus,
            individual.biometricDeduplicationBatchStatus,
            deduplicationBatchDict,
          )
        )}
      </TableCell>
      <TableCell align="left">
        {individual.biometricDeduplicationGoldenRecordResults?.length ||
        individual.deduplicationGoldenRecordsResults?.length ? (
          <DedupeBiographicalBiometricResults
            status={renderDeduplicationStatus(
              individual.deduplicationGoldenRecordStatus,
              individual.biometricDeduplicationGoldenRecordStatus,
              deduplicationGoldenDict,
            )}
            results={individual.deduplicationGoldenRecordResults}
            biometricResults={
              individual.biometricDeduplicationGoldenRecordResults
            }
            individual={individual}
          />
        ) : (
          renderDeduplicationStatus(
            individual.deduplicationGoldenRecordResults,
            individual.biometricDeduplicationGoldenRecordResults,
            deduplicationGoldenDict,
          )
        )}
      </TableCell>
    </ClickableTableRow>
  );
}
