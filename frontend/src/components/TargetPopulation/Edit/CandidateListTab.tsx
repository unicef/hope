import React from 'react';
import { Typography, Paper } from '@material-ui/core';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { FieldArray } from 'formik';
import { TargetingCriteria } from '../TargetingCriteria';
import { Results } from '../Results';
import { useGoldenRecordByTargetingCriteriaQuery } from '../../../__generated__/graphql';
import { Label } from '@material-ui/icons';
import styled from 'styled-components';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

export function CandidateListTab({values}) {
  return (
    <>
      <FieldArray
        name='candidateListCriterias'
        render={(arrayHelpers) => (
          <TargetingCriteria
            helpers={arrayHelpers}
            candidateListRules={values.candidateListCriterias}
            isEdit
          />
        )}
      />
      <Results />
      {values.candidateListCriterias.length ? (
        <TargetPopulationHouseholdTable
          variables={{
            targetingCriteria: {
              rules: values.candidateListCriterias.map((rule) => {
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
          }}
          query={useGoldenRecordByTargetingCriteriaQuery}
          queryObjectName='goldenRecordByTargetingCriteria'
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            Target Population Entries (Households)
          </Typography>
          <Label>Add targeting criteria to see results.</Label>
        </PaperContainer>
      )}
    </>
  );
}
