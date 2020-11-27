import React from 'react';
import { Typography, Paper } from '@material-ui/core';
import { FieldArray } from 'formik';
import { Label } from '@material-ui/icons';
import styled from 'styled-components';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { TargetingCriteria } from '../TargetingCriteria';
import { Results } from '../Results';
import { useGoldenRecordByTargetingCriteriaQuery } from '../../../__generated__/graphql';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

export function CandidateListTab({ values }: { values }): React.ReactElement {
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
            ...getTargetingCriteriaVariables({
              criterias: values.candidateListCriterias,
            }),
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
