import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  AllRegistrationDataImportsQueryVariables,
  RegistrationDataImportNode,
  useAllRegistrationDataImportsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './RegistrationDataImportTableHeadCells';
import { RegistrationDataImportTableRow } from './RegistrationDataImportTableRow';
import moment from 'moment';

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
    importedBy_Id: filter.importedBy !== '' ? filter.importedBy : undefined,
    status: filter.status !== '' ? filter.status : undefined,
  };
  return (
    <TableWrapper>
      <UniversalTable<
        RegistrationDataImportNode,
        AllRegistrationDataImportsQueryVariables
      >
        title='List of Imports'
        headCells={headCells}
        query={useAllRegistrationDataImportsQuery}
        queriedObjectName='allRegistrationDataImports'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <RegistrationDataImportTableRow registrationDataImport={row} />
        )}
      />
    </TableWrapper>
  );
}
