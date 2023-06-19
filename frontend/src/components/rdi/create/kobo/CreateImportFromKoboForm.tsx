/* eslint-disable react-hooks/exhaustive-deps */
import { CircularProgress } from '@material-ui/core';
import { Field, FormikProvider, useFormik } from 'formik';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ImportDataStatus,
  useCreateRegistrationKoboImportMutation,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { handleValidationErrors } from '../../../../utils/utils';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { KoboImportDataRepresentation } from './KoboImportDataRepresentation';
import { KoboProjectSelect } from './KoboProjectSelect';
import { useSaveKoboImportDataAndCheckStatus } from './useSaveKoboImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(2, 'Too short')
    .max(255, 'Too long'),
});
export function CreateImportFromKoboForm({
  setSubmitForm,
  setSubmitDisabled,
}): React.ReactElement {
  const {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveKoboLoading,
    koboImportData,
  } = useSaveKoboImportDataAndCheckStatus();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const history = useHistory();
  const { baseUrl, businessArea } = useBaseUrl();
  const [createImport] = useCreateRegistrationKoboImportMutation();
  const onSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            importDataId: koboImportData.id,
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
            businessAreaSlug: businessArea,
          },
        },
      });
      history.push(
        `/${baseUrl}/registration-data-import/${data.data.registrationKoboImport.registrationDataImport.id}`,
      );
    } catch (error) {
      const { nonValidationErrors } = handleValidationErrors(
        'registrationXlsxImport',
        error,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(
          t('Unexpected problem while creating Registration Data Import'),
        );
      }
    }
  };
  const formik = useFormik({
    initialValues: {
      name: '',
      koboAssetId: '',
      onlyActiveSubmissions: true,
      screenBeneficiary: false,
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
      onlyActiveSubmissions: formik.values.onlyActiveSubmissions,
      koboAssetId: formik.values.koboAssetId,
    });
  };
  useEffect(() => stopPollingImportData, []);
  useEffect(() => {
    saveKoboInputData();
  }, [formik.values.koboAssetId, formik.values.onlyActiveSubmissions]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (koboImportData?.status === ImportDataStatus.Finished) {
      setSubmitDisabled(false);
    }
  }, [koboImportData]);
  return (
    <div>
      <FormikProvider value={formik}>
        <Field
          name='onlyActiveSubmissions'
          label={t('Only approved submissions')}
          color='primary'
          component={FormikCheckboxField}
        />
        <Field
          name='pullPictures'
          label={t('Pull pictures')}
          color='primary'
          component={FormikCheckboxField}
        />
        <KoboProjectSelect />
        <Field
          name='name'
          fullWidth
          label={t('Title')}
          required
          variant='outlined'
          component={FormikTextField}
        />
        <ScreenBeneficiaryField />
        <CircularProgressContainer>
          {saveKoboLoading && <CircularProgress />}
        </CircularProgressContainer>
        <KoboImportDataRepresentation
          koboImportData={koboImportData}
          loading={saveKoboLoading}
        />
      </FormikProvider>
    </div>
  );
}
