import { ReactElement } from 'react';
import styled from 'styled-components';
import {
  AllActiveProgramsQueryVariables,
  AllProgramsQuery,
  ProgrammeChoiceDataQuery,
  useAllActiveProgramsQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './LookUpProgrammesHeadCellsSurveys';
import { LookUpProgrammesTableRowSurveys } from './LookUpProgrammesTableRowSurveys';

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

interface LookUpProgrammesTableSurveysProps {
  businessArea: string;
  filter;
  choicesData: ProgrammeChoiceDataQuery;
  selectedProgram;
  handleChange: (value) => void;
  setFieldValue;
}

export function LookUpProgrammesTableSurveys({
  businessArea,
  filter,
  choicesData,
  selectedProgram,
  handleChange,
  setFieldValue,
}: LookUpProgrammesTableSurveysProps): ReactElement {
  const initialVariables: AllActiveProgramsQueryVariables = {
    businessArea,
    search: filter.search,
    startDate: filter.startDate || null,
    endDate: filter.endDate || null,
    status: filter.status,
    sector: filter.sector,
    numberOfHouseholdsWithTpInProgram: JSON.stringify({
      min: filter.numberOfHouseholdsMin || 1,
      max: filter.numberOfHouseholdsMax,
    }),
    budget: JSON.stringify(filter.budget),
    dataCollectingType: filter.dataCollectingType,
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
    setFieldValue('program', id);
  };

  return (
    <NoTableStyling>
      <TableWrapper>
        <UniversalTable<
          AllProgramsQuery['allPrograms']['edges'][number]['node'],
          AllActiveProgramsQueryVariables
        >
          headCells={headCells}
          query={useAllActiveProgramsQuery}
          queriedObjectName="allActivePrograms"
          initialVariables={initialVariables}
          renderRow={(row) => (
            <LookUpProgrammesTableRowSurveys
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
}
