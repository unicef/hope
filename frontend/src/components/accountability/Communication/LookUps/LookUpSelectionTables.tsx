import React from 'react';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { RegistrationDataImportTable } from '../../../../containers/tables/rdi/RegistrationDataImportTable';
import { TargetPopulationTable } from '../../../../containers/tables/targeting/TargetPopulationTable';
import { usePermissions } from '../../../../hooks/usePermissions';
import { CommunicationTabsValues } from '../../../../utils/constants';
import { HouseholdChoiceDataQuery } from '../../../../__generated__/graphql';
import { LookUpHouseholdTable } from '../../../grievances/LookUps/LookUpHouseholdTable/LookUpHouseholdTable';

interface LookUpSelectionTablesProps {
  selectedTab: number;
  choicesData: HouseholdChoiceDataQuery;
  values;
  filtersHouseholdApplied;
  filtersTargetPopulationApplied;
  filtersRDIApplied;
  businessArea;
  onValueChange;
  handleChange;
}
export function LookUpSelectionTables({
  selectedTab,
  choicesData,
  values,
  filtersHouseholdApplied,
  filtersTargetPopulationApplied,
  filtersRDIApplied,
  businessArea,
  onValueChange,
  handleChange,
}: LookUpSelectionTablesProps): React.ReactElement {
  const permissions = usePermissions();

  return (
    <>
      {selectedTab === CommunicationTabsValues.HOUSEHOLD && (
        <LookUpHouseholdTable
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
        <TargetPopulationTable
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
        <RegistrationDataImportTable
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
