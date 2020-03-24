/* eslint-disable react-hooks/exhaustive-deps */
import React, { useCallback, useState } from 'react';
import styled from 'styled-components';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@material-ui/core';
import ExitToAppRoundedIcon from '@material-ui/icons/ExitToAppRounded';
import { useDropzone } from 'react-dropzone';
import { Field, Form, Formik } from 'formik';
import get from 'lodash/get';
import {
  useCreateRegistrationDataImportMutation,
  useUploadImportDataXlsxFileMutation,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { LoadingComponent } from '../../../components/LoadingComponent';
import { FormikTagsSelectField } from '../../../shared/Formik/FormikTagsSelectField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
const ComboBox = styled(Select)`
  & {
    min-width: 200px;
  }
`;
const DropzoneContainer = styled.div`
  width: 100%;
  height: 100px;
  background-color: rgba(2, 62, 144, 0.1);
  color: #023e90;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing(5)}px;
  cursor: pointer;

  ${({ disabled }) => (disabled ? 'filter: grayscale(100%);' : '')}
`;

function DropzoneField({ onChange, loading }) {
  const onDrop = useCallback((acceptedFiles) => {
    onChange(acceptedFiles);
  }, []);
  const { getRootProps, getInputProps, acceptedFiles, rootRef } = useDropzone({
    disabled: loading,
    accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    onDrop,
  });
  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;
  return (
    <div>
      <DropzoneContainer {...getRootProps()} disabled={loading}>
        <LoadingComponent isLoading={loading} absolute />
        <input {...getInputProps()} />
        {acceptedFilename || 'UPLOAD FILE'}
      </DropzoneContainer>
    </div>
  );
}

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name Upload is required'),
});

export function RegistrationDataImport(): React.ReactElement {
  const [open, setOpen] = useState(false);

  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [
    uploadMutate,
    { data: uploadData, loading: fileLoading },
  ] = useUploadImportDataXlsxFileMutation();
  const [createRegistrationMutate] = useCreateRegistrationDataImportMutation();
  const [importType, setImportType] = useState();
  const { t } = useTranslation();
  let counters = null;
  if (get(uploadData, 'uploadImportDataXlsxFile.importData')) {
    counters = (
      <>
        <div>
          {uploadData.uploadImportDataXlsxFile.importData.numberOfHouseholds}{' '}
          Households available to Import
        </div>
        <div>
          {uploadData.uploadImportDataXlsxFile.importData.numberOfIndividuals}{' '}
          Individuals available to Import
        </div>
      </>
    );
  }
  let importTypeSpecificContent = null;
  if (importType === 'excel') {
    importTypeSpecificContent = (
      <>
        <DropzoneField
          loading={fileLoading}
          onChange={(files) => {
            if (files.length === 0) {
              return;
            }
            const file = files[0];
            const fileSizeMB = file.size / (1024 * 1024);
            if (fileSizeMB > 200) {
              showMessage(
                `File size is to big. It should be under 200MB, File size is ${fileSizeMB}MB`,
              );
              return;
            }
            uploadMutate({
              variables: {
                file,
              },
            });
          }}
        />
      </>
    );
  }

  return (
    <span>
      <Button
        variant='contained'
        color='primary'
        startIcon={<ExitToAppRoundedIcon />}
        onClick={() => setOpen(true)}
      >
        IMPORT
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <Formik
          validationSchema={validationSchema}
          onSubmit={async (values) => {
            console.log('values', values);
            const { data } = await createRegistrationMutate({
              variables: {
                registrationDataImportData: {
                  importDataId:
                    uploadData.uploadImportDataXlsxFile.importData.id,
                  name: values.name,
                },
              },
            });
            showMessage('Registration', {
              pathname: `/${businessArea}/registration-data-import/${data.createRegistrationDataImport.registrationDataImport.id}`,
              historyMethod: 'push',
            });
          }}
          initialValues={{ name: '' }}
        >
          {({ submitForm, values }) => (
            <Form>
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  <Typography variant='h6'>
                    {t('Select File to Import')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  Are you sure you want to activate this Programme and push data
                  to CashAssist?
                </DialogDescription>

                <FormControl variant='filled' margin='dense'>
                  <InputLabel>Import from</InputLabel>
                  <ComboBox
                    value={importType}
                    variant='filled'
                    label=''
                    onChange={(e) => setImportType(e.target.value)}
                    fullWidth
                  >
                    <MenuItem key='excel' value='excel'>
                      Excel
                    </MenuItem>
                    <MenuItem key='kobo' value='kobo'>
                      Kobo
                    </MenuItem>
                  </ComboBox>
                </FormControl>
                {importTypeSpecificContent}
                {counters}
                <Field
                  name='name'
                  fullWidth
                  label='Name Upload'
                  required
                  component={FormikTextField}
                />
                <Field
                  name='tags'
                  fullWidth
                  label='Tags'
                  required
                  component={FormikTagsSelectField}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>CANCEL</Button>
                  <Button
                    type='submit'
                    color='primary'
                    variant='contained'
                    disabled={!uploadData}
                    onClick={() => {
                      submitForm();
                    }}
                  >
                    {t('IMPORT')}
                  </Button>
                </DialogActions>
              </DialogFooter>
            </Form>
          )}
        </Formik>
      </Dialog>
    </span>
  );
}
