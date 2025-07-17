import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CreateTargetPopulationHeader from '@components/targeting/CreateTargetPopulation/CreateTargetPopulationHeader';
import Exclusions from '@components/targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '@components/targeting/PaperContainer';
import AddFilterTargetingCriteriaDisplay from '@components/targeting/TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Divider, Grid2 as Grid, Typography } from '@mui/material';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  getTargetingCriteriaVariables,
  HhIndIdValidation,
} from '@utils/targetingUtils';
import { showApiErrorMessages } from '@utils/utils';
import { Field, FieldArray, Form, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

const CreateTargetPopulationPage = (): ReactElement => {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const { isSocialDctType, isStandardDctType } = useProgramContext();
  const initialValues = {
    name: '',
    criterias: [],
    program: programId,
    programCycleId: {
      value: '',
      name: '',
    },
    excludedIds: '',
    exclusionReason: '',
    flagExcludeIfActiveAdjudicationTicket: false,
    flagExcludeIfOnSanctionList: false,
    householdIds: '',
    individualIds: '',
    deliveryMechanism: '',
    fsp: '',
  };
  const { mutateAsync: createTargetPopulation, isPending: loadingCreate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        programSlug,
        requestBody,
      }: {
        businessAreaSlug: string;
        programSlug: string;
        requestBody;
      }) =>
        RestService.restBusinessAreasProgramsTargetPopulationsCreate({
          businessAreaSlug,
          programSlug,
          requestBody,
        }),
    });
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const navigate = useNavigate();

  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessArea,
      }),
  });

  if (permissions === null) return null;
  if (!businessAreaData) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const screenBeneficiary = businessAreaData?.screenBeneficiary;
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Targeting Name is required'))
      .min(3, t('Targeting Name should have at least 3 characters.'))
      .max(255, t('Targeting Name should have at most 255 characters.')),
    excludedIds: HhIndIdValidation,
    exclusionReason: Yup.string().max(500, t('Too long')),
    programCycleId: Yup.object().shape({
      value: Yup.string().required('Programme Cycle is required'),
    }),
  });

  const handleSubmit = async (values): Promise<void> => {
    const fsp = values.criterias[0]?.fsp || null;
    const deliveryMechanism = values.criterias[0]?.deliveryMechanism || null;
    const requestBody = {
      programCycleId: values.programCycleId.value,
      name: values.name,
      excludedIds: values.excludedIds,
      exclusionReason: values.exclusionReason,
      fspId: fsp,
      deliveryMechanismCode: deliveryMechanism,
      ...getTargetingCriteriaVariables(values),
    };

    try {
      const res = await createTargetPopulation({
        businessAreaSlug: businessArea,
        programSlug: programId,
        requestBody,
      });
      showMessage(t('Target Population Created'));
      navigate(`/${baseUrl}/target-population/${res.id}`);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values, setFieldValue, errors }) => {
        return (
          <Form>
            <AutoSubmitFormOnEnter />
            <CreateTargetPopulationHeader
              handleSubmit={submitForm}
              loading={loadingCreate}
              values={values}
              baseUrl={baseUrl}
              permissions={permissions}
            />
            <PaperContainer>
              <Box pt={3} pb={3}>
                <Typography variant="h6">{t('Targeting Criteria')}</Typography>
              </Box>
              <Grid container mb={5}>
                <Grid size={{ xs: 6 }}>
                  <ProgramCycleAutocompleteRest
                    value={values.programCycleId}
                    onChange={async (e) => {
                      await setFieldValue('programCycleId', e);
                    }}
                    required
                    // @ts-ignore
                    error={errors.programCycleId?.value}
                  />
                </Grid>
              </Grid>
              <Grid container>
                <Grid size={{ xs: 6 }}>
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
              {values.program ? (
                <FieldArray
                  name="criterias"
                  render={(arrayHelpers) => (
                    <AddFilterTargetingCriteriaDisplay
                      helpers={arrayHelpers}
                      rules={values.criterias}
                      screenBeneficiary={screenBeneficiary}
                      isStandardDctType={isStandardDctType}
                      isSocialDctType={isSocialDctType}
                      isEdit
                    />
                  )}
                />
              ) : null}
            </PaperContainer>
            <Exclusions />

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
        );
      }}
    </Formik>
  );
};

export default withErrorBoundary(
  CreateTargetPopulationPage,
  'CreateTargetPopulationPage',
);
