import { Box, Divider, Grid, Typography } from '@mui/material';
import { Field, FieldArray, Form, Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ProgramStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
  useAllProgramsForChoicesQuery,
  useUpdateTpMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '@utils/targetingUtils';
import { getFullNodeFromEdgesById } from '@utils/utils';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { Exclusions } from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import { TargetingCriteria } from '../TargetingCriteria';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { FormikTextField } from '@shared/Formik/FormikTextField';

const Label = styled.p`
  color: #b1b1b5;
`;

interface EditTargetPopulationProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  screenBeneficiary: boolean;
}

export const EditTargetPopulation = ({
  targetPopulation,
  screenBeneficiary,
}: EditTargetPopulationProps): React.ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
    flagExcludeIfActiveAdjudicationTicket:
      targetPopulation.targetingCriteria
        .flagExcludeIfActiveAdjudicationTicket || false,
    flagExcludeIfOnSanctionList:
      targetPopulation.targetingCriteria.flagExcludeIfOnSanctionList || false,
    householdIds: targetPopulation.targetingCriteria.householdIds,
    individualIds: targetPopulation.targetingCriteria.individualIds,
  };
  const [mutate, { loading }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { isSocialDctType, isStandardDctType } = useProgramContext();
  const { data: allProgramsData, loading: loadingPrograms } =
    useAllProgramsForChoicesQuery({
      variables: { businessArea, status: [ProgramStatus.Active] },
      fetchPolicy: 'cache-and-network',
    });

  if (loadingPrograms) {
    return <LoadingComponent />;
  }
  if (!allProgramsData) {
    return null;
  }

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length) {
      errors.targetingCriteria = t(
        'You need to select at least one targeting criteria',
      );
    }
    return errors;
  };
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(3, 'Targeting name should have at least 3 characters.')
      .max(255, 'Targeting name should have at most 255 characters.'),
    excludedIds: Yup.string().test(
      'testName',
      'ID is not in the correct format',
      (ids) => {
        if (!ids?.length) {
          return true;
        }
        const idsArr = ids.split(',');
        return idsArr.every((el) =>
          /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el),
        );
      },
    ),
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            id: values.id,
            programId: values.program,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              flagExcludeIfActiveAdjudicationTicket:
                values.flagExcludeIfActiveAdjudicationTicket,
              flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
              criterias: values.targetingCriteria,
            }),
          },
        },
      });
      showMessage(t('Target Population Updated'));
      navigate(`/${baseUrl}/target-population/${values.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const selectedProgram = (values): void =>
    getFullNodeFromEdgesById(
      allProgramsData?.allPrograms?.edges,
      values.program,
    );

  const category =
    targetPopulation.targetingCriteria?.rules.length !== 0 ? 'filters' : 'ids';
  const isTitleEditable = (): boolean => targetPopulation.status !== 'LOCKED';

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, submitForm }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <EditTargetPopulationHeader
            handleSubmit={submitForm}
            values={values}
            loading={loading}
            baseUrl={baseUrl}
            targetPopulation={targetPopulation}
            category={category}
          />
          <PaperContainer>
            <Box pt={3} pb={3}>
              <Typography variant="h6">{t('Targeting Criteria')}</Typography>
            </Box>
            <Grid container>
              <Grid item xs={6}>
                <Field
                  name="name"
                  label={t('Target Population Name')}
                  type="text"
                  fullWidth
                  required
                  component={FormikTextField}
                  variant="outlined"
                  data-cy="input-name"
                />
              </Grid>
            </Grid>
            <Box pt={6} pb={6}>
              <Divider />
            </Box>
            {category === 'filters' ? (
              <FieldArray
                name="targetingCriteria"
                render={(arrayHelpers) => (
                  <TargetingCriteria
                    helpers={arrayHelpers}
                    rules={values.targetingCriteria}
                    selectedProgram={selectedProgram(values)}
                    isEdit
                    screenBeneficiary={screenBeneficiary}
                    isStandardDctType={isStandardDctType}
                    isSocialDctType={isSocialDctType}
                    category={category}
                  />
                )}
              />
            ) : null}
          </PaperContainer>
          {category === 'filters' && (
            <Exclusions initialOpen={Boolean(values.excludedIds)} />
          )}
          ,
          <Box
            pt={3}
            pb={3}
            display="flex"
            flexDirection="column"
            alignItems="center"
          >
            <Typography style={{ color: '#b1b1b5' }} variant="h6">
              {t('Save to see the list of households')}
            </Typography>
            <Typography style={{ color: '#b1b1b5' }} variant="subtitle1">
              {t('List of households will be available after saving')}
            </Typography>
          </Box>
        </Form>
      )}
    </Formik>
  );
};
