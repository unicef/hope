import moment from 'moment';
import React, { ReactElement } from 'react';
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

export const RegistrationDataImportTable = ({
  filter,
  canViewDetails,
}): ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables = {
    search: filter.search,
    importDate: filter.importDate
      ? moment(filter.importDate).format('YYYY-MM-DD')
      : null,
    importedBy: filter.importedBy
      ? decodeIdString(filter.importedBy)
      : undefined,
    status: filter.status !== '' ? filter.status : undefined,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<
        RegistrationDataImportNode,
        AllRegistrationDataImportsQueryVariables
      >
        title={t('List of Imports')}
        getTitle={(data) =>
          `${t('List of Imports')} (${
            data.allRegistrationDataImports.totalCount
          })`
        }
        headCells={headCells}
        defaultOrderBy='importDate'
        defaultOrderDirection='desc'
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllRegistrationDataImportsQuery}
        queriedObjectName='allRegistrationDataImports'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <RegistrationDataImportTableRow
            key={row.id}
            registrationDataImport={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
