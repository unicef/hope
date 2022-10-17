import React from 'react';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { LookUpProgrammesTable } from '../../../../containers/tables/LookUpProgrammesTable/LookUpProgrammesTable';
import { TargetPopulationTable } from '../../../../containers/tables/targeting/TargetPopulationTable';
import { usePermissions } from '../../../../hooks/usePermissions';
import { SurveyTabsValues } from '../../../../utils/constants';
import { ProgrammeChoiceDataQuery } from '../../../../__generated__/graphql';

interface LookUpSelectionTablesProps {
  selectedTab: number;
  choicesData: ProgrammeChoiceDataQuery;
  values;
  filtersProgramApplied;
  filtersTargetPopulationApplied;
  businessArea: string;
  onValueChange;
  handleChange;
}
export function LookUpSelectionTables({
  selectedTab,
  choicesData,
  values,
  filtersProgramApplied,
  filtersTargetPopulationApplied,
  businessArea,
  onValueChange,
  handleChange,
}: LookUpSelectionTablesProps): React.ReactElement {
  const permissions = usePermissions();

  return (
    <>
      {selectedTab === SurveyTabsValues.PROGRAM && (
        <LookUpProgrammesTable
          businessArea={businessArea}
          filter={filtersProgramApplied}
          choicesData={choicesData}
          selectedProgram={values.program}
          handleChange={(value) => {
            handleChange(SurveyTabsValues.PROGRAM, value);
          }}
          setFieldValue={onValueChange}
        />
      )}
      {selectedTab === SurveyTabsValues.TARGET_POPULATION && (
        <TargetPopulationTable
          filter={filtersTargetPopulationApplied}
          canViewDetails={hasPermissions(
            PERMISSIONS.TARGETING_VIEW_DETAILS,
            permissions,
          )}
          enableRadioButton
          selectedTargetPopulation={values.targetPopulation}
          handleChange={(value) => {
            handleChange(SurveyTabsValues.TARGET_POPULATION, value);
          }}
          noTableStyling
          noTitle
        />
      )}
    </>
  );
}
