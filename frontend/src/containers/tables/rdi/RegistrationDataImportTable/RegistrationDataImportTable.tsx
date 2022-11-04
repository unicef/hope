import moment from 'moment';
import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../../utils/utils';
import {
  AllRegistrationDataImportsQueryVariables,
  RegistrationDataImportNode,
  useAllRegistrationDataImportsQuery,
} from '../../../../__generated__/graphql';
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
  const businessArea = useBusinessArea();
  const initialVariables = {
    // eslint-disable-next-line @typescript-eslint/camelcase
    name_Icontains: filter.search,
    importDate: filter.importDate
      ? moment(filter.importDate).format('YYYY-MM-DD')
      : null,
    // eslint-disable-next-line @typescript-eslint/camelcase
    importedBy_Id: filter.importedBy
      ? decodeIdString(filter.importedBy)
      : undefined,
    status: filter.status !== '' ? filter.status : undefined,
    businessArea,
    importDateRange: JSON.stringify(filter.importDateRange),
    size: JSON.stringify(filter.size),
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): React.ReactElement => {
    return (
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
          defaultOrderBy='importDate'
          defaultOrderDirection='desc'
          rowsPerPageOptions={[10, 15, 20]}
          query={useAllRegistrationDataImportsQuery}
          queriedObjectName='allRegistrationDataImports'
          initialVariables={initialVariables}
          renderRow={(row) => (
            <RegistrationDataImportTableRow
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
  };
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
