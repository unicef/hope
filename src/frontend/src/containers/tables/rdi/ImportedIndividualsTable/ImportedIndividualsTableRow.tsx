import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { sexToCapitalize } from '@utils/utils';
import { ReactElement } from 'react';
import { DedupeBiographicalBiometricResults } from '@components/rdi/details/DedupeBiographicalBiometricResults';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { BiometricDeduplicationGoldenRecordStatusEnum } from '@restgenerated/models/BiometricDeduplicationGoldenRecordStatusEnum';
import { BiometricDeduplicationBatchStatusEnum } from '@restgenerated/models/BiometricDeduplicationBatchStatusEnum';
import { DeduplicationBatchStatusEnum } from '@restgenerated/models/DeduplicationBatchStatusEnum';
import { DeduplicationGoldenRecordStatusEnum } from '@restgenerated/models/DeduplicationGoldenRecordStatusEnum';

interface ImportedIndividualsTableRowProps {
  individual: IndividualList;
  rdi;
}

export function ImportedIndividualsTableRow({
  individual,
  rdi,
}: ImportedIndividualsTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl, businessArea } = useBaseUrl();

  const individualDetailsPath = `/${baseUrl}/population/individuals/${individual.id}`;

  const handleClick = (): void => {
    navigate(individualDetailsPath, {
      state: {
        breadcrumbTitle: `Registration Data Import: ${rdi.name}`,
        breadcrumbUrl: `/${businessArea}/registration-data-import/${rdi.id}`,
      },
    });
  };

  const WORST_STATUS_PRIORITY: (
    | BiometricDeduplicationGoldenRecordStatusEnum
    | BiometricDeduplicationBatchStatusEnum
    | DeduplicationBatchStatusEnum
    | DeduplicationGoldenRecordStatusEnum
  )[] = [
    BiometricDeduplicationGoldenRecordStatusEnum.DUPLICATE,
    BiometricDeduplicationBatchStatusEnum.DUPLICATE_IN_BATCH,
    BiometricDeduplicationGoldenRecordStatusEnum.NEEDS_ADJUDICATION,
    BiometricDeduplicationBatchStatusEnum.SIMILAR_IN_BATCH,
    BiometricDeduplicationGoldenRecordStatusEnum.NOT_PROCESSED,
    BiometricDeduplicationBatchStatusEnum.NOT_PROCESSED,
    BiometricDeduplicationGoldenRecordStatusEnum.POSTPONE,
    BiometricDeduplicationGoldenRecordStatusEnum.UNIQUE,
    BiometricDeduplicationBatchStatusEnum.UNIQUE_IN_BATCH,
  ];

  function renderDeduplicationStatus(
    goldenRecordStatus:
      | BiometricDeduplicationGoldenRecordStatusEnum
      | DeduplicationGoldenRecordStatusEnum
      | BiometricDeduplicationBatchStatusEnum
      | DeduplicationBatchStatusEnum,
    batchStatus:
      | BiometricDeduplicationBatchStatusEnum
      | DeduplicationBatchStatusEnum
      | BiometricDeduplicationGoldenRecordStatusEnum
      | DeduplicationGoldenRecordStatusEnum,
    dict,
  ): string {
    const indexGoldenRecordStatus =
      WORST_STATUS_PRIORITY.indexOf(goldenRecordStatus);
    const indexBatchStatus = WORST_STATUS_PRIORITY.indexOf(batchStatus);
    if (indexGoldenRecordStatus === -1 && indexBatchStatus === -1) {
      return '';
    }
    if (indexGoldenRecordStatus === -1) {
      return dict[batchStatus];
    }
    if (indexBatchStatus === -1) {
      return dict[goldenRecordStatus];
    }
    if (indexGoldenRecordStatus < indexBatchStatus) {
      return dict[goldenRecordStatus];
    }
    return dict[batchStatus];
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
      <TableCell align="left">{individual.role}</TableCell>
      <TableCell align="left">{individual.relationshipDisplay}</TableCell>
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
              {
                [individual.deduplicationBatchStatus]:
                  individual.deduplicationBatchStatusDisplay,
                [individual.biometricDeduplicationBatchStatus]:
                  individual.biometricDeduplicationBatchStatusDisplay,
              },
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
            {
              [individual.deduplicationBatchStatus]:
                individual.deduplicationBatchStatusDisplay,
              [individual.biometricDeduplicationBatchStatus]:
                individual.biometricDeduplicationBatchStatusDisplay,
            },
          )
        )}
      </TableCell>
      <TableCell align="left">
        {individual.biometricDeduplicationGoldenRecordResults?.length ||
        individual.deduplicationGoldenRecordResults?.length ? (
          <DedupeBiographicalBiometricResults
            status={renderDeduplicationStatus(
              individual.deduplicationGoldenRecordStatus,
              individual.biometricDeduplicationGoldenRecordStatus,
              {
                [individual.deduplicationGoldenRecordStatus]:
                  individual.deduplicationGoldenRecordStatusDisplay,
                [individual.biometricDeduplicationGoldenRecordStatus]:
                  individual.biometricDeduplicationGoldenRecordStatusDisplay,
              },
            )}
            results={individual.deduplicationGoldenRecordResults}
            biometricResults={
              individual.biometricDeduplicationGoldenRecordResults
            }
            individual={individual}
          />
        ) : (
          renderDeduplicationStatus(
            individual.deduplicationGoldenRecordStatus,
            individual.biometricDeduplicationGoldenRecordStatus,
            {
              [individual.deduplicationGoldenRecordStatus]:
                individual.deduplicationGoldenRecordStatusDisplay,
              [individual.biometricDeduplicationGoldenRecordStatus]:
                individual.biometricDeduplicationGoldenRecordStatusDisplay,
            },
          )
        )}
      </TableCell>
    </ClickableTableRow>
  );
}
