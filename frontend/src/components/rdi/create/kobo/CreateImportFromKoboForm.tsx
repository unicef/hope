/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { Field, FormikProvider, useFormik } from 'formik';
import { CircularProgress } from '@material-ui/core';
import styled from 'styled-components';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { useSaveKoboImportDataAndCheckStatus } from './useSaveKoboImportDataAndCheckStatus';
import { KoboProjectSelect } from './KoboProjectSelect';
import { KoboImportDataRepresentation } from './KoboImportDataRepresentation';

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
    saveAndStartPulling,
    stopPullingImportData,
    loading: saveKoboLoading,
    koboImportData,
  } = useSaveKoboImportDataAndCheckStatus();
  const onSubmit = (): void => {
    console.log('on submit');
  };
  const { t } = useTranslation();
  const businessAreaSlug = useBusinessArea();
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
    stopPullingImportData();
    await saveAndStartPulling({
      businessAreaSlug,
      onlyActiveSubmissions: formik.values.onlyActiveSubmissions,
      koboAssetId: formik.values.koboAssetId,
    });
  };
  useEffect(() => stopPullingImportData, []);
  useEffect(() => {
    saveKoboInputData();
  }, [formik.values.koboAssetId, formik.values.onlyActiveSubmissions]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
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
