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
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
<<<<<<< HEAD
=======
import {
  ImportDataStatus,
  useAllActiveProgramsQuery,
  useCreateRegistrationKoboImportMutation
} from '../../../../__generated__/graphql';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {LoadingComponent} from "../../../core/LoadingComponent";
import {FormikSelectField} from "../../../../shared/Formik/FormikSelectField";
import { useSaveKoboImportDataAndCheckStatus } from './useSaveKoboImportDataAndCheckStatus';
import { KoboProjectSelect } from './KoboProjectSelect';
>>>>>>> 6bba15b0bb56ca008d12ef456e490df910b96e3e
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
  programId: Yup.string()
    .required('Programme Name is required')
    .min(2, 'Too short')
    .max(150, 'Too long'),
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

  const { data: programData, loading } = useAllActiveProgramsQuery({
    variables: {
      first: 100,
      businessArea: businessAreaSlug
    }
  });

  const onSubmit = async (values): Promise<void> => {
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            importDataId: koboImportData.id,
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
<<<<<<< HEAD
            businessAreaSlug: businessArea,
=======
            businessAreaSlug,
            programId: values.programId
>>>>>>> 6bba15b0bb56ca008d12ef456e490df910b96e3e
          },
        },
      });
      history.push(
        `/${baseUrl}/registration-data-import/${data.data.registrationKoboImport.registrationDataImport.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };
  const formik = useFormik({
    initialValues: {
      name: '',
      koboAssetId: '',
      onlyActiveSubmissions: true,
      screenBeneficiary: false,
      programId: ''
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

  if (loading) {
    return <LoadingComponent />
  }

  const mappedProgramChoices = programData?.allActivePrograms?.edges?.map(
      (element) => ({name: element.node.name, value: element.node.id})
  );

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
        <Field
          name='programId'
          label={t('Program Name')}
          fullWidth
          variant='outlined'
          required
          choices={mappedProgramChoices}
          component={FormikSelectField}
          data-cy='input-data-program-name'
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
