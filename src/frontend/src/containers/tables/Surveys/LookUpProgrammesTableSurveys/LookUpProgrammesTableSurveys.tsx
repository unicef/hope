import { ReactElement, useState, useEffect, useMemo } from 'react';
import styled from 'styled-components';
import { ProgrammeChoiceDataQuery } from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from './LookUpProgrammesHeadCellsSurveys';
import { LookUpProgrammesTableRowSurveys } from './LookUpProgrammesTableRowSurveys';
import { adjustHeadCells } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { ProgramList } from '@restgenerated/models/ProgramList';

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
  const { selectedProgram: programFromContext } = useProgramContext();
  const beneficiaryGroup = programFromContext?.beneficiaryGroup;

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status !== '' ? filter.status : undefined,
      sector: filter.sector,
      numberOfHouseholdsMax: filter.numberOfHouseholdsMax,
      numberOfHouseholdsMin: filter.numberOfHouseholdsMin || 1,
      budgetMax: filter.budgetMax,
      budgetMin: filter.budgetMin,
      dataCollectingType: filter.dataCollectingType,
      ordering: 'startDate',
    }),
    [
      businessArea,
      filter.search,
      filter.startDate,
      filter.endDate,
      filter.status,
      filter.sector,
      filter.numberOfHouseholdsMin,
      filter.numberOfHouseholdsMax,
      filter.budgetMin,
      filter.budgetMax,
      filter.dataCollectingType,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    error: errorPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: ['businessAreasProgramsList', queryVariables, businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsList(
        createApiParams({ businessAreaSlug: businessArea }, queryVariables, {
          withPagination: true,
        }),
      ),
    enabled: !!queryVariables.businessAreaSlug,
  });

  const handleRadioChange = (id: string): void => {
    handleChange(id);
    setFieldValue('program', id);
  };

  const replacements = {
    totalHhCount: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <NoTableStyling>
      <TableWrapper>
        <UniversalRestTable
          headCells={adjustedHeadCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          defaultOrderBy="startDate"
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          error={errorPrograms}
          renderRow={(row: ProgramList) => (
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
