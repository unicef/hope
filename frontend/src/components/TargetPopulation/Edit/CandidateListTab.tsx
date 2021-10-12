import {
  Box,
  Button,
  Collapse,
  Grid,
  Paper,
  Typography,
} from '@material-ui/core';
import { Label } from '@material-ui/icons';
import KeyboardArrowDown from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUp from '@material-ui/icons/KeyboardArrowUp';
import { Field, FieldArray } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/TargetPopulationHouseholdTable';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
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
  const [isExclusionsOpen, setExclusionsOpen] = useState(
    Boolean(values.excludedIds),
  );
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
      <PaperContainer>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>
            {t(
              'Excluded Target Population Entries (Households or Individuals)',
            )}
          </Typography>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setExclusionsOpen(!isExclusionsOpen)}
            endIcon={
              isExclusionsOpen ? <KeyboardArrowUp /> : <KeyboardArrowDown />
            }
          >
            {isExclusionsOpen ? t('HIDE') : t('SHOW')}
          </Button>
        </Box>
        <Collapse in={isExclusionsOpen}>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                <Field
                  name='excludedIds'
                  fullWidth
                  variant='outlined'
                  label={t('Household or Individual IDs to exclude')}
                  component={FormikTextField}
                />
              </Grid>
            </Grid>
          </Box>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                <Field
                  name='exclusionReason'
                  fullWidth
                  multiline
                  variant='outlined'
                  label={t('Exclusion Reason')}
                  component={FormikTextField}
                />
              </Grid>
            </Grid>
          </Box>
        </Collapse>
      </PaperContainer>
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
