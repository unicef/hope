/* eslint-disable react-hooks/exhaustive-deps */
import { Box, CircularProgress } from '@mui/material';
import { Field, FormikProvider, useFormik } from 'formik';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ImportDataStatus,
  useCreateRegistrationXlsxImportMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { DropzoneField } from './DropzoneField';
import { XlsxImportDataRepresentation } from './XlsxImportDataRepresentation';
import { useSaveXlsxImportDataAndCheckStatus } from './useSaveXlsxImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  height: 50px;
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(4, 'Too short')
    .max(255, 'Too long'),
});
export function CreateImportFromXlsxForm({
  setSubmitForm,
  setSubmitDisabled,
}): React.ReactElement {
  const {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveXlsxLoading,
    xlsxImportData,
  } = useSaveXlsxImportDataAndCheckStatus();
  const { baseUrl, businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [createImport] = useCreateRegistrationXlsxImportMutation();

  const onSubmit = async (values): Promise<void> => {
    setSubmitDisabled(true);
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            importDataId: xlsxImportData.id,
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
            businessAreaSlug: businessArea,
            allowDeliveryMechanismsValidationErrors:
              values.allowDeliveryMechanismsValidationErrors,
          },
        },
      });
      navigate(
        `/${baseUrl}/registration-data-import/${data.data.registrationXlsxImport.registrationDataImport.id}`,
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
      file: null,
      allowDeliveryMechanismsValidationErrors: false,
    },
    validationSchema,
    onSubmit,
  });
  // eslint-disable-next-line @typescript-eslint/require-await
  const saveXlsxInputData = async (): Promise<void> => {
    if (!formik.values.file) {
      return;
    }
    setSubmitDisabled(true);
    stopPollingImportData();
    await saveAndStartPolling({
      businessAreaSlug: businessArea,
      file: formik.values.file,
    });
  };
  useEffect(() => stopPollingImportData, []);
  useEffect(() => {
    saveXlsxInputData();
  }, [formik.values.file]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (
      xlsxImportData?.status === ImportDataStatus.Finished ||
      (xlsxImportData?.status ===
        ImportDataStatus.DeliveryMechanismsValidationError &&
        formik.values.allowDeliveryMechanismsValidationErrors)
    ) {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }, [xlsxImportData, formik.values.allowDeliveryMechanismsValidationErrors]);

  return (
    <FormikProvider value={formik}>
      <DropzoneField loading={saveXlsxLoading} />
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
      <Box mt={2}>
        {xlsxImportData?.status ===
          ImportDataStatus.DeliveryMechanismsValidationError && (
          <Box mt={2}>
            <Field
              name="allowDeliveryMechanismsValidationErrors"
              fullWidth
              label={t('Allow Delivery Mechanisms Validation Errors')}
              variant="outlined"
              component={FormikCheckboxField}
            />
          </Box>
        )}
      </Box>
      <ScreenBeneficiaryField />
      {saveXlsxLoading ? (
        <CircularProgressContainer>
          <CircularProgress />
        </CircularProgressContainer>
      ) : (
        <XlsxImportDataRepresentation
          xlsxImportData={xlsxImportData}
          loading={saveXlsxLoading}
        />
      )}
    </FormikProvider>
  );
}
