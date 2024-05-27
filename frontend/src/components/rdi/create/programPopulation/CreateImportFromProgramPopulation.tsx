/* eslint-disable react-hooks/exhaustive-deps */
import { LoadingComponent } from '@components/core/LoadingComponent';
import {
  useAllProgramsForChoicesQuery,
  useCreateRegistrationProgramPopulationImportMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FormikProvider, useFormik } from 'formik';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import * as Yup from 'yup';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(4, 'Too short')
    .max(255, 'Too long'),
  program: Yup.string().required('Programme is required'),
});

export const CreateImportFromProgramPopulationForm = ({
  setSubmitForm,
  setSubmitDisabled,
}): React.ReactElement => {
  const { baseUrl, businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [createImport] = useCreateRegistrationProgramPopulationImportMutation();
  const { data: programsData, loading: programsDataLoading } =
    useAllProgramsForChoicesQuery({
      variables: {
        first: 100,
        businessArea,
        compatibleDct: true,
      },
    });

  const onSubmit = async (values): Promise<void> => {
    setSubmitDisabled(true);
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
            importFromProgramId: values.program,
            businessAreaSlug: businessArea,
          },
        },
      });
      navigate(
        `/${baseUrl}/registration-data-import/${data.data.registrationProgramPopulationImport.registrationDataImport.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
      setSubmitDisabled(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      screenBeneficiary: false,
      program: '',
    },
    validationSchema,
    onSubmit,
  });

  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);

  if (programsDataLoading) return <LoadingComponent />;
  if (!programsData) return null;

  const mappedProgramChoices = programsData?.allPrograms?.edges?.map(
    (element) => ({ name: element.node.name, value: element.node.id }),
  );

  return (
    <FormikProvider value={formik}>
      <Box mt={2}>
        <Field
          name="name"
          fullWidth
          label={t('Title')}
          required
          variant="outlined"
          component={FormikTextField}
        />
      </Box>
      <ScreenBeneficiaryField />
      <Box mt={2}>
        <Field
          name="program"
          label={t('Programme Name')}
          fullWidth
          variant="outlined"
          choices={mappedProgramChoices}
          component={FormikSelectField}
        />
      </Box>
    </FormikProvider>
  );
};
