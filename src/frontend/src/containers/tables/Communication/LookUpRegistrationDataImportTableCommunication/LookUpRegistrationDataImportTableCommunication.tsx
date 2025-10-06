import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import styled from 'styled-components';
import { RestService } from '@restgenerated/services/RestService';
import type { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';
import type { PaginatedRegistrationDataImportListList } from '@restgenerated/models/PaginatedRegistrationDataImportListList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { decodeIdString } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './LookUpRegistrationDataImportTableHeadCellsCommunication';
import { LookUpRegistrationDataImportTableRowCommunication } from './LookUpRegistrationDataImportTableRowCommunication';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface LookUpRegistrationDataImportTableCommunicationProps {
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

function LookUpRegistrationDataImportTableCommunication({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedRDI,
  handleChange,
  noTableStyling,
  noTitle,
}: LookUpRegistrationDataImportTableCommunicationProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const initialQueryVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programSlug: programId,
      search: filter.search,
      importedById: filter.importedBy
        ? decodeIdString(filter.importedBy)
        : undefined,
      status: filter.status !== '' ? filter.status : undefined,
      importDateRange: JSON.stringify({
        min: filter.importDateRangeMin || null,
        max: filter.importDateRangeMax || null,
      }),
      totalHouseholdsCountWithValidPhoneNoMin:
        filter.totalHouseholdsCountWithValidPhoneNoMin || undefined,
      totalHouseholdsCountWithValidPhoneNoMax:
        filter.totalHouseholdsCountWithValidPhoneNoMax || undefined,
    };
  }, [
    businessArea,
    programId,
    filter.search,
    filter.importedBy,
    filter.status,
    filter.importDateRangeMin,
    filter.importDateRangeMax,
    filter.totalHouseholdsCountWithValidPhoneNoMin,
    filter.totalHouseholdsCountWithValidPhoneNoMax,
  ]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } =
    useQuery<PaginatedRegistrationDataImportListList>({
      queryKey: [
        'businessAreasProgramsRegistrationDataImportsList',
        queryVariables,
        programId,
        businessArea,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsRegistrationDataImportsList(
          createApiParams(
            { businessAreaSlug: businessArea, programSlug: programId },
            queryVariables,
            { withPagination: true },
          ),
        ),
    });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsRegistrationDataImportsCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRegistrationDataImportsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
  });

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderRow = (
    registrationDataImport: RegistrationDataImportList,
  ): ReactElement => (
    <LookUpRegistrationDataImportTableRowCommunication
      key={registrationDataImport.id}
      radioChangeHandler={enableRadioButton && handleRadioChange}
      selectedRDI={selectedRDI}
      registrationDataImport={registrationDataImport}
      canViewDetails={canViewDetails}
    />
  );

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable
        title={noTitle ? null : t('List of Imports')}
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        renderRow={renderRow}
        data={data}
        error={error}
        isLoading={isLoading}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={countData?.count}
      />
    </TableWrapper>
  );

  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}

export default withErrorBoundary(
  LookUpRegistrationDataImportTableCommunication,
  'LookUpRegistrationDataImportTableCommunication',
);
