import React from 'react';
import { FieldArray } from 'formik';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { TargetingCriteria } from '../TargetingCriteria';
import { Results } from '../Results';
import { useFinalHouseholdsListByTargetingCriteriaQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export function TargetPopulationTab({ values }): React.ReactElement {
  const businessArea = useBusinessArea();
  return (
    <>
      <FieldArray
        name='targetPopulationCriterias'
        render={(arrayHelpers) => (
          <TargetingCriteria
            helpers={arrayHelpers}
            candidateListRules={values.candidateListCriterias}
            isEdit
          />
        )}
      />
      <Results />

      <TargetPopulationHouseholdTable
        variables={{
          targetPopulation: values.id,
          businessArea,
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
