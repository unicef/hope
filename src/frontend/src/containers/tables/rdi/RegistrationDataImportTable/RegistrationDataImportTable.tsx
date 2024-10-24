import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllRegistrationDataImportsQueryVariables,
  RegistrationDataImportNode,
  useAllRegistrationDataImportsQuery,
  useDeduplicationFlagsQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString, decodeIdString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';

interface RegistrationDataImportProps {
  filter;
  canViewDetails: boolean;
  enableRadioButton?: boolean;
  selectedRDI?;
  handleChange?;
  noTableStyling?;
  noTitle?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function RegistrationDataImportTable({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedRDI,
  handleChange,
  noTableStyling,
  noTitle,
}: RegistrationDataImportProps): ReactElement {
  const { t } = useTranslation();
  const { data: deduplicationFlags } = useDeduplicationFlagsQuery({
    fetchPolicy: 'cache-and-network',
  });
  const { businessArea, programId } = useBaseUrl();
  const initialVariables = {
    search: filter.search,
    importedBy: filter.importedBy
      ? decodeIdString(filter.importedBy)
      : undefined,
    status: filter.status !== '' ? filter.status : undefined,
    businessArea,
    program: programId,
    importDateRange: JSON.stringify({
      min: dateToIsoString(filter.importDateRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.importDateRangeMax, 'endOfDay'),
    }),
    size: JSON.stringify({ min: filter.sizeMin, max: filter.sizeMax }),
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const prepareHeadCells = () => {
    let header = headCells.slice();
    if (deduplicationFlags?.canRunDeduplication) {
      header.splice(4, 0, {
        disablePadding: false,
        label: 'Biometric Deduplicated',
        id: 'biometricDeduplicated',
        numeric: false,
        disableSort: true,
      });
    }

    if (!enableRadioButton) {
      header = header.slice(1);
    }
    return header;
  };

  const renderTable = (): React.ReactElement => (
    <TableWrapper>
      <UniversalTable<
        RegistrationDataImportNode,
        AllRegistrationDataImportsQueryVariables
      >
        title={noTitle ? null : t('List of Imports')}
        getTitle={(data) =>
          noTitle
            ? null
            : `${t('List of Imports')} (${
                data?.allRegistrationDataImports?.totalCount || 0
              })`
        }
        headCells={prepareHeadCells()}
        defaultOrderBy="importDate"
        defaultOrderDirection="desc"
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllRegistrationDataImportsQuery}
        queriedObjectName="allRegistrationDataImports"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <RegistrationDataImportTableRow
            key={row.id}
            radioChangeHandler={enableRadioButton && handleRadioChange}
            selectedRDI={selectedRDI}
            registrationDataImport={row}
            canViewDetails={canViewDetails}
            biometricDeduplicationEnabled={
              deduplicationFlags?.canRunDeduplication
            }
          />
        )}
      />
    </TableWrapper>
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
