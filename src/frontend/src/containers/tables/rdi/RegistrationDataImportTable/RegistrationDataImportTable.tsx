import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useState, useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import {
  headCells,
  headCellsPeople,
} from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedRegistrationDataImportListList } from '@restgenerated/models/PaginatedRegistrationDataImportListList';
import { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';

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

function RegistrationDataImportTable({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedRDI,
  handleChange,
  noTableStyling,
  noTitle,
}: RegistrationDataImportProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { businessAreaSlug, programSlug, businessArea, programId } =
    useBaseUrl();

  const { data: deduplicationFlags } = useQuery({
    queryKey: ['deduplicationFlags', businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsDeduplicationFlagsRetrieve({
        businessAreaSlug,
        slug: programSlug,
      }),
  });

  const initialVariables = useMemo(
    () => ({
      search: filter.search,
      importedById: filter.importedBy || undefined,
      status: filter.status !== '' ? filter.status : undefined,
      businessArea,
      program: programId,
      importDateAfter: filter.importDateRangeMin,
      importDateBefore: filter.importDateRangeMax,
      sizeMin: filter.sizeMin,
      sizeMax: filter.sizeMax,
    }),
    [
      filter.importDateRangeMax,
      filter.importDateRangeMin,
      filter.importedBy,
      filter.search,
      filter.sizeMax,
      filter.sizeMin,
      filter.status,
      businessArea,
      programId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialVariables);

  useEffect(() => {
    setQueryVariables(initialVariables);
  }, [initialVariables]);

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const replacements = {
    numberOfIndividuals: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.memberLabelPlural}`,
    numberOfHouseholds: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
    household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
  };

  const adjustedHeadCells = adjustHeadCells(
    isSocialDctType ? headCellsPeople : headCells,
    beneficiaryGroup,
    replacements,
  );

  const prepareHeadCells = () => {
    if (isSocialDctType) {
      return enableRadioButton ? adjustedHeadCells : adjustedHeadCells.slice(1);
    }
    let header = adjustedHeadCells.slice();
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

  const [page, setPage] = useState(0);

  const {
    data: listData,
    isLoading,
    error,
  } = useQuery<PaginatedRegistrationDataImportListList>({
    queryKey: [
      'businessAreasProgramsRegistrationDataImportsList',
      businessArea,
      programSlug,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRegistrationDataImportsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug },
          queryVariables,
          { withPagination: true },
        ),
      ),
  });

  const { data: countData } = useQuery<{ count: number }>({
    queryKey: [
      'businessAreasProgramsRegistrationDataImportsCount',
      businessArea,
      programSlug,
      queryVariables,
    ],
    queryFn: async () => {
      const params = createApiParams(
        { businessAreaSlug: businessArea, programSlug },
        queryVariables,
        { withPagination: false },
      );
      return RestService.restBusinessAreasProgramsRegistrationDataImportsCountRetrieve(
        params,
      );
    },
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable<RegistrationDataImportList, any>
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
        title={noTitle ? null : `${t('List of Imports')} (${itemsCount || 0})`}
        itemsCount={itemsCount || 0}
        headCells={prepareHeadCells()}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={listData}
        isLoading={isLoading}
        error={error}
        page={page}
        setPage={setPage}
      />
    </TableWrapper>
  );
  return (
    <>
      {noTableStyling ? (
        <NoTableStyling>{renderTable()}</NoTableStyling>
      ) : (
        renderTable()
      )}
    </>
  );
}
export default withErrorBoundary(
  RegistrationDataImportTable,
  'RegistrationDataImportTable',
);
