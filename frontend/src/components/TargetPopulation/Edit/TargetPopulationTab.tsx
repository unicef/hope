import React from 'react';
import { FieldArray } from 'formik';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { TargetingCriteria } from '../TargetingCriteria';
import { Results } from '../Results';
import { useFinalHouseholdsListByTargetingCriteriaQuery } from '../../../__generated__/graphql';

export function TargetPopulationTab({
  values,
  selectedTab,
}): React.ReactElement {
  return (
    <>
      <FieldArray
        name='targetPopulationCriterias'
        render={(arrayHelpers) => (
          <TargetingCriteria
            helpers={arrayHelpers}
            candidateListRules={values.candidateListCriterias}
            targetPopulationRules={values.targetPopulationCriterias}
            selectedTab={selectedTab}
            isEdit
          />
        )}
      />
      <Results />

      <TargetPopulationHouseholdTable
        variables={{
          targetPopulation: values.id,
          ...(values.targetPopulationCriterias.length && {
            targetingCriteria: {
              rules: values.targetPopulationCriterias.map((rule) => {
                return {
                  filters: rule.filters.map((each) => {
                    return {
                      comparisionMethod: each.comparisionMethod,
                      arguments: each.arguments,
                      fieldName: each.fieldName,
                      isFlexField: each.isFlexField,
                      headOfHousehold: each.headOfHousehold,
                    };
                  }),
                };
              }),
            },
          }),
        }}
        query={useFinalHouseholdsListByTargetingCriteriaQuery}
        queryObjectName='finalHouseholdsListByTargetingCriteria'
      />
    </>
  );
}
