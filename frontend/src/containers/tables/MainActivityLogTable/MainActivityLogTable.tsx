import React from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './MainActivityLogTableHeadCells';
import { MainActivityLogTableRow } from './MainActivityLogTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;
interface MainActivityLogTableProps {
  businessArea: string;
}
export const MainActivityLogTable = ({
  businessArea,
}: MainActivityLogTableProps): React.ReactElement => {
  const initialVariables = {
    businessArea,
  };
  return <TableWrapper>MAIN ACTIVITY LOG TABLE</TableWrapper>;
};
