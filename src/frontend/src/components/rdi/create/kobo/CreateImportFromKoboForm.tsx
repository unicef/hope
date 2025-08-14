/* eslint-disable react-hooks/exhaustive-deps */
import { CircularProgress } from '@mui/material';
import { Field, FormikProvider, useFormik } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { Status753Enum } from '@restgenerated/models/Status753Enum';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation } from '@tanstack/react-query';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { KoboImportDataRepresentation } from './KoboImportDataRepresentation';
import { KoboProjectSelect } from './KoboProjectSelect';
import { useSaveKoboImportDataAndCheckStatus } from './useSaveKoboImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  width: 100%;
  height: 50px;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(4, 'Too short')
    .max(255, 'Too long'),
});
export function CreateImportFromKoboForm({
  setSubmitForm,
  setSubmitDisabled,
}): ReactElement {
  const {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveKoboLoading,
    koboImportData,
  } = useSaveKoboImportDataAndCheckStatus();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { baseUrl, businessArea, programId } = useBaseUrl();

  // Mutation for creating registration kobo import
  const createImportMutation = useMutation({
    mutationFn: async (data: { 
      importDataId: string; 
      name: string; 
      screenBeneficiary: boolean;
      pullPictures: boolean;
    }) => {
      return RestService.restBusinessAreasProgramsRegistrationDataImportsRegistrationKoboImportCreate({
        businessAreaSlug: businessArea,
        programSlug: programId,
        requestBody: data,
      });
    },
    onSuccess: (data) => {
      navigate(`/${baseUrl}/registration-data-import/${data.id}`);
    },
    onError: (error: any) => {
      showMessage(error.message || 'Error creating kobo import');
    },
  });

  const onSubmit = async (values): Promise<void> => {
    console.log('Kobo onSubmit called with values:', values);
    if (!koboImportData?.id) {
      return;
    }
    
    createImportMutation.mutate({
      importDataId: koboImportData.id,
      name: values.name,
      screenBeneficiary: values.screenBeneficiary,
      pullPictures: values.pullPictures,
    });
  };
  const formik = useFormik({
    initialValues: {
      name: '',
      koboAssetId: '',
      onlyActiveSubmissions: true,
      screenBeneficiary: false,
      pullPictures: true,
    },
    validationSchema,
    onSubmit,
  });
  const saveKoboInputData = async (): Promise<void> => {
    if (!formik.values.koboAssetId) {
      return;
    }
    setSubmitDisabled(true);
    stopPollingImportData();
    await saveAndStartPolling({
      businessAreaSlug: businessArea,
      programSlug: programId,
      onlyActiveSubmissions: formik.values.onlyActiveSubmissions,
      koboAssetId: formik.values.koboAssetId,
      pullPictures: formik.values.pullPictures,
    });
  };
  useEffect(() => stopPollingImportData, []);
  useEffect(() => {
    saveKoboInputData();
  }, [
    formik.values.koboAssetId,
    formik.values.onlyActiveSubmissions,
    formik.values.pullPictures,
  ]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (
      koboImportData?.status === Status753Enum.FINISHED) {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }, [koboImportData]);

  return (
    <div>
      <FormikProvider value={formik}>
        <Field
          name="onlyActiveSubmissions"
          label={t('Only approved submissions')}
          color="primary"
          component={FormikCheckboxField}
        />
        <Field
          name="pullPictures"
          label={t('Pull pictures')}
          color="primary"
          component={FormikCheckboxField}
        />
        <KoboProjectSelect />
        <Field
          name="name"
          fullWidth
          label={t('Title')}
          required
          variant="outlined"
          component={FormikTextField}
        />
        <ScreenBeneficiaryField />
        {saveKoboLoading ? (
          <CircularProgressContainer>
            <CircularProgress />
          </CircularProgressContainer>
        ) : (
          <KoboImportDataRepresentation
            koboImportData={koboImportData}
            loading={saveKoboLoading}
          />
        )}
      </FormikProvider>
    </div>
  );
}
