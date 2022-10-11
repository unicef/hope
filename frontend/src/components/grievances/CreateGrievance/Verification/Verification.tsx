import { Box, Typography } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { Consent } from '../../Consent';
import { HouseholdQuestionnaire } from '../../HouseholdQuestionnaire/HouseholdQuestionnaire';
import { IndividualQuestionnaire } from '../../IndividualQuestionnnaire/IndividualQuestionnaire';

const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export interface VerificationProps {
  values;
}

export const Verification = ({
  values,
}: VerificationProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <BoxWithBorders>
      {values.selectedHousehold && (
        <>
          <Typography variant='subtitle1'>
            {t('Select correctly answered questions (minimum 5)')}
          </Typography>
          <Box py={4}>
            <Typography variant='subtitle2'>
              {t('Household Questionnaire')}
            </Typography>
            <Box py={4}>
              <HouseholdQuestionnaire values={values} />
            </Box>
          </Box>
          <Typography variant='subtitle2'>
            {t('Individual Questionnaire')}
          </Typography>
          <Box py={4}>
            <IndividualQuestionnaire values={values} />
          </Box>
          <BoxWithBorderBottom />
        </>
      )}
      <Consent />
      <Field
        name='consent'
        label={t('Received Consent*')}
        color='primary'
        fullWidth
        container={false}
        component={FormikCheckboxField}
      />
    </BoxWithBorders>
  );
};
