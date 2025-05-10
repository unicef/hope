import { ProgrammeChoiceDataQuery } from '@generated/graphql';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { LookUpProgrammesTableSurveys } from '@containers/tables/Surveys/LookUpProgrammesTableSurveys/LookUpProgrammesTableSurveys';
import { LookUpTargetPopulationTableSurveys } from '@containers/tables/Surveys/LookUpTargetPopulationTableSurveys';
import { usePermissions } from '@hooks/usePermissions';
import { SurveyTabsValues } from '@utils/constants';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface LookUpSelectionTablesSurveysProps {
  selectedTab: number;
  choicesData: ProgrammeChoiceDataQuery;
  values;
  filtersProgramApplied;
  filtersTargetPopulationApplied;
  businessArea: string;
  onValueChange;
  handleChange;
}
function LookUpSelectionTablesSurveys({
  selectedTab,
  choicesData,
  values,
  filtersProgramApplied,
  filtersTargetPopulationApplied,
  businessArea,
  onValueChange,
  handleChange,
}: LookUpSelectionTablesSurveysProps): ReactElement {
  const permissions = usePermissions();

  return (
    <>
      {selectedTab === SurveyTabsValues.PROGRAM && (
        <LookUpProgrammesTableSurveys
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
        <LookUpTargetPopulationTableSurveys
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

export default withErrorBoundary(
  LookUpSelectionTablesSurveys,
  'LookUpSelectionTablesSurveys',
);
