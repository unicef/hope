import { Paper, Typography } from '@material-ui/core';
import { Label } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { useGoldenRecordByTargetingCriteriaQuery } from '../../../__generated__/graphql';
import { Results } from '../Results';
import { TargetingCriteria } from '../TargetingCriteria';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

export function CandidateListTab({
  values,
  selectedProgram,
  businessArea,
}: {
  values;
  selectedProgram?;
  businessArea?;
}): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <FieldArray
        name='candidateListCriterias'
        render={(arrayHelpers) => (
          <TargetingCriteria
            helpers={arrayHelpers}
            candidateListRules={values.candidateListCriterias}
            isEdit
            selectedProgram={selectedProgram}
          />
        )}
      />
      <Results />
      {values.candidateListCriterias.length && selectedProgram ? (
        <TargetPopulationHouseholdTable
          variables={{
            ...getTargetingCriteriaVariables({
              criterias: values.candidateListCriterias,
            }),
            program: selectedProgram.id,
            excludedIds: values.excludedIds,
            businessArea,
          }}
          query={useGoldenRecordByTargetingCriteriaQuery}
          queryObjectName='goldenRecordByTargetingCriteria'
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            {t('Target Population Entries (Households)')}
          </Typography>
          <Label>{t('Add targeting criteria to see results.')}</Label>
        </PaperContainer>
      )}
    </>
  );
}
