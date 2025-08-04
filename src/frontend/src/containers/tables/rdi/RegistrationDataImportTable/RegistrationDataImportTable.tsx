import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';

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
  const { selectedProgram } = useProgramContext();
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
      size:
        filter.sizeMin || filter.sizeMax
          ? JSON.stringify({ min: filter.sizeMin, max: filter.sizeMax })
          : undefined,
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
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const prepareHeadCells = () => {
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
  });

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestQueryTable
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
        title={
          noTitle ? null : `${t('List of Imports')} (${countData?.count || 0})`
        }
        itemsCount={countData?.count || 0}
        headCells={prepareHeadCells()}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        query={RestService.restBusinessAreasProgramsRegistrationDataImportsList}
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
