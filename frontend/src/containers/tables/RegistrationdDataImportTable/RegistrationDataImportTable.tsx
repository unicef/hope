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

const TableWrapper = styled.div`
  padding: 20px;
`;

export function RegistrationDataImportTable(): ReactElement {
  const initialVariables = {};
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
