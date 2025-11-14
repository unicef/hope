import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { LookUpTargetPopulationTableSurveys } from '@containers/tables/Surveys/LookUpTargetPopulationTableSurveys';
import { usePermissions } from '@hooks/usePermissions';
import { SurveyTabsValues } from '@utils/constants';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface LookUpSelectionTablesSurveysProps {
  selectedTab: number;
  values;
  filtersTargetPopulationApplied;
  handleChange;
}
const LookUpSelectionTablesSurveys = ({
  selectedTab,
  values,
  filtersTargetPopulationApplied,
  handleChange,
}: LookUpSelectionTablesSurveysProps): ReactElement => {
  const permissions = usePermissions();

  return (
    <>
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
};

export default withErrorBoundary(
  LookUpSelectionTablesSurveys,
  'LookUpSelectionTablesSurveys',
);
