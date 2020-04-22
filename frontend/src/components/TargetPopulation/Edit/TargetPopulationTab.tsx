import React from 'react';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { FieldArray } from 'formik';
import { TargetingCriteria } from '../TargetingCriteria';
import { Results } from '../Results';
import { useFinalHouseholdsListByTargetingCriteriaQuery } from '../../../__generated__/graphql';

export function TargetPopulationTab({ values, selectedTab }) {
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
          id: values.id,
          ...(values.targetPopulationCriterias.length && {
            targetingCriteria: {
              rules: values.criterias.map((rule) => {
                return {
                  filters: rule.filters.map((each) => {
                    return {
                      comparisionMethod: each.comparisionMethod,
                      arguments: each.arguments,
                      fieldName: each.fieldName,
                      isFlexField: each.isFlexField,
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
