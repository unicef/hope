import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllRegistrationDataImportsQueryVariables,
  RegistrationDataImportNode,
  useAllRegistrationDataImportsQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { decodeIdString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
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
  const initialVariables = {
    search: filter.search,
    program: programId,
    importedBy: filter.importedBy
      ? decodeIdString(filter.importedBy)
      : undefined,
    status: filter.status !== '' ? filter.status : undefined,
    businessArea,
    importDateRange: JSON.stringify({
      min: filter.importDateRangeMin || null,
      max: filter.importDateRangeMax || null,
    }),
    totalHouseholdsCountWithValidPhoneNoMin:
      filter.totalHouseholdsCountWithValidPhoneNoMin || null,
    totalHouseholdsCountWithValidPhoneNoMax:
      filter.totalHouseholdsCountWithValidPhoneNoMax || null,
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): ReactElement => (
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
                data.allRegistrationDataImports.totalCount
              })`
        }
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        defaultOrderBy="importDate"
        defaultOrderDirection="desc"
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllRegistrationDataImportsQuery}
        queriedObjectName="allRegistrationDataImports"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpRegistrationDataImportTableRowCommunication
            key={row.id}
            radioChangeHandler={enableRadioButton && handleRadioChange}
            selectedRDI={selectedRDI}
            registrationDataImport={row}
            canViewDetails={canViewDetails}
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

export default withErrorBoundary(
  LookUpRegistrationDataImportTableCommunication,
  'LookUpRegistrationDataImportTableCommunication',
);
