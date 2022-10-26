import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import {
  AllActiveProgramsQueryVariables,
  ProgrammeChoiceDataQuery,
  ProgramNode,
  useAllProgramsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './LookUpProgrammesHeadCells';
import { LookUpProgrammesTableRow } from './LookUpProgrammesTableRow';

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

interface LookUpProgrammesTableProps {
  businessArea: string;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
  selectedProgram;
  handleChange: (value) => void;
  setFieldValue;
}

export const LookUpProgrammesTable = ({
  businessArea,
  filter,
  choicesData,
  selectedProgram,
  handleChange,
  setFieldValue,
}: LookUpProgrammesTableProps): ReactElement => {
  const initialVariables: AllActiveProgramsQueryVariables = {
    businessArea,
    search: filter.search,
    startDate: filter.startDate,
    endDate: filter.endDate,
    status: filter.status,
    sector: filter.sector,
    numberOfHouseholds: JSON.stringify(filter.numberOfHouseholds),
    budget: JSON.stringify(filter.budget),
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
    setFieldValue('program', id);
  };

  return (
    <NoTableStyling>
      <TableWrapper>
        <UniversalTable<ProgramNode, AllActiveProgramsQueryVariables>
          headCells={headCells}
          query={useAllProgramsQuery}
          queriedObjectName='allActivePrograms'
          initialVariables={initialVariables}
          renderRow={(row) => (
            <LookUpProgrammesTableRow
              key={row.id}
              program={row}
              choicesData={choicesData}
              radioChangeHandler={handleRadioChange}
              selectedProgram={selectedProgram}
            />
          )}
        />
      </TableWrapper>
    </NoTableStyling>
  );
};
