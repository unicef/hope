import { Box, Typography } from '@mui/material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { Consent } from '../../Consent';
import HouseholdQuestionnaire from '../../HouseholdQuestionnaire/HouseholdQuestionnaire';
import IndividualQuestionnaire from '../../IndividualQuestionnnaire/IndividualQuestionnaire';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

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

function Verification({ values }: VerificationProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <BoxWithBorders>
      <>
        {/* //TODO: Optional for now */}
        {/* {(values.selectedHousehold || values.selectedIndividual) && (
          <Typography variant='subtitle1'>
            {t('Select correctly answered questions (minimum 5)')}
          </Typography>
        )} */}
        {values.selectedHousehold && !isSocialDctType && (
          <Box py={4}>
            <Typography variant="subtitle2">
              {`${beneficiaryGroup?.groupLabel} Questionnaire`}
            </Typography>
            <Box py={4}>
              <HouseholdQuestionnaire values={values} />
            </Box>
          </Box>
        )}
        {values.selectedIndividual && (
          <>
            <Typography variant="subtitle2">
              {`${beneficiaryGroup?.memberLabel} Questionnaire`}
            </Typography>
            <Box py={4}>
              <IndividualQuestionnaire values={values} />
            </Box>
            <BoxWithBorderBottom />
          </>
        )}
      </>
      <Consent />
      <Field
        name="consent"
        label={t('Received Consent')}
        color="primary"
        required
        fullWidth
        container={false}
        component={FormikCheckboxField}
      />
    </BoxWithBorders>
  );
}

export default withErrorBoundary(Verification, 'Verification');
