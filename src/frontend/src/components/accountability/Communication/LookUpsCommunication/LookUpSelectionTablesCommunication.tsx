import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import LookUpHouseholdTableCommunication from '@containers/tables/Communication/LookUpHouseholdTableCommunication/LookUpHouseholdTableCommunication';
import { usePermissions } from '@hooks/usePermissions';
import { CommunicationTabsValues } from '@utils/constants';
import { ReactElement } from 'react';
import LookUpTargetPopulationTableCommunication from '@containers/tables/Communication/LookUpTargetPopulationTableCommunication/LookUpTargetPopulationTableCommunication';
import LookUpRegistrationDataImportTableCommunication from '@containers/tables/Communication/LookUpRegistrationDataImportTableCommunication/LookUpRegistrationDataImportTableCommunication';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

interface LookUpSelectionTablesCommunicationProps {
  selectedTab: number;
  choicesData: HouseholdChoices;
  values;
  filtersHouseholdApplied;
  filtersTargetPopulationApplied;
  filtersRDIApplied;
  businessArea: string;
  onValueChange;
  handleChange;
}
export function LookUpSelectionTablesCommunication({
  selectedTab,
  choicesData,
  values,
  filtersHouseholdApplied,
  filtersTargetPopulationApplied,
  filtersRDIApplied,
  businessArea,
  onValueChange,
  handleChange,
}: LookUpSelectionTablesCommunicationProps): ReactElement {
  const permissions = usePermissions();

  return (
    <>
      {selectedTab === CommunicationTabsValues.HOUSEHOLD && (
        <LookUpHouseholdTableCommunication
          filter={filtersHouseholdApplied}
          businessArea={businessArea}
          choicesData={choicesData}
          noTableStyling
          setFieldValue={onValueChange}
          selectedHousehold={values.households}
          setSelectedHousehold={(value) => {
            handleChange(CommunicationTabsValues.HOUSEHOLD, value);
          }}
          householdMultiSelect
        />
      )}
      {selectedTab === CommunicationTabsValues.TARGET_POPULATION && (
        <LookUpTargetPopulationTableCommunication
          filter={filtersTargetPopulationApplied}
          canViewDetails={hasPermissions(
            PERMISSIONS.TARGETING_VIEW_DETAILS,
            permissions,

          )}
          enableRadioButton
          selectedTargetPopulation={values.targetPopulation}
          handleChange={(value) => {
            handleChange(CommunicationTabsValues.TARGET_POPULATION, value);
          }}
          noTableStyling
          noTitle
        />
      )}
      {selectedTab === CommunicationTabsValues.RDI && (
        <LookUpRegistrationDataImportTableCommunication
          filter={filtersRDIApplied}
          canViewDetails={hasPermissions(
            PERMISSIONS.RDI_VIEW_DETAILS,
            permissions,
          )}
          enableRadioButton
          selectedRDI={values.registrationDataImport}
          handleChange={(value) => {
            handleChange(CommunicationTabsValues.RDI, value);
          }}
          noTableStyling
          noTitle
        />
      )}
    </>
  );
}
