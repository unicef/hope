import React, { ReactElement } from 'react';
import styled from 'styled-components';
import moment from 'moment';
import {
  AllRegistrationDataImportsQueryVariables,
  RegistrationDataImportNode,
  useAllRegistrationDataImportsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../tables/UniversalTable';
import { decodeIdString } from '../../../../utils/utils';
import { headCells } from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

export function RegistrationDataImportTable({ filter }): ReactElement {
  const initialVariables = {
    // eslint-disable-next-line @typescript-eslint/camelcase
    name_Icontains: filter.search,
    importDate:
      filter.importDate && moment(filter.importDate).format('YYYY-MM-DD'),
    // eslint-disable-next-line @typescript-eslint/camelcase
    importedBy_Id: filter.importedBy
      ? decodeIdString(filter.importedBy)
      : undefined,
    status: filter.status !== '' ? filter.status : undefined,
  };
  return (
    <TableWrapper>
      <UniversalTable<
        RegistrationDataImportNode,
        AllRegistrationDataImportsQueryVariables
      >
        title='List of Imports'
        getTitle={(data) =>
          `List of Import (${data.allRegistrationDataImports.totalCount})`
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
          />
        )}
      />
    </TableWrapper>
  );
}
