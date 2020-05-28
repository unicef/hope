/* eslint-disable react-hooks/exhaustive-deps */
import React, { useCallback, useState } from 'react';
import styled from 'styled-components';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import {
  Button,
  CardActions,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@material-ui/core';
import ExpandMoreRoundedIcon from '@material-ui/icons/ExpandMoreRounded';
import ExpandLessRoundedIcon from '@material-ui/icons/ExpandLessRounded';

import ExitToAppRoundedIcon from '@material-ui/icons/ExitToAppRounded';
import { useDropzone } from 'react-dropzone';
import { Field, Form, Formik } from 'formik';
import get from 'lodash/get';
import {
  KoboErrorNode,
  SaveKoboImportDataMutation,
  UploadImportDataXlsxFileMutation,
  useAllKoboProjectsQuery,
  useCreateRegistrationKoboImportMutation,
  useCreateRegistrationXlsxImportMutation,
  useSaveKoboImportDataMutation,
  useUploadImportDataXlsxFileMutation,
  XlsxRowErrorNode,
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

const StyledDialogFooter = styled(DialogFooter)`
  && {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
`;
const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
`;
const ErrorsContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

function DropzoneField({ onChange, loading }): React.ReactElement {
  const onDrop = useCallback((acceptedFiles) => {
    onChange(acceptedFiles);
  }, []);
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
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

function Errors({
  errors,
}: {
  errors: XlsxRowErrorNode[];
}): React.ReactElement {
  const [expanded, setExpanded] = useState(false);
  if (!errors || !errors.length) {
    return null;
  }
  return (
    <>
      <ErrorsContainer>
        <Error>Errors</Error>
        <IconButton
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          aria-label='show more'
        >
          {expanded ? <ExpandLessRoundedIcon /> : <ExpandMoreRoundedIcon />}
        </IconButton>
      </ErrorsContainer>
      <Collapse in={expanded} timeout='auto' unmountOnExit>
        {errors.map((item) => (
          <Error>
            <strong>Row: {item.rowNumber}</strong> {item.message}
          </Error>
        ))}
      </Collapse>
    </>
  );
}
function ErrorsKobo({
  errors,
}: {
  errors: KoboErrorNode[];
}): React.ReactElement {
  const [expanded, setExpanded] = useState(false);
  if (!errors || !errors.length) {
    return null;
  }
  return (
    <>
      <ErrorsContainer>
        <Error>Errors</Error>
        <IconButton
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          aria-label='show more'
        >
          {expanded ? <ExpandLessRoundedIcon /> : <ExpandMoreRoundedIcon />}
        </IconButton>
      </ErrorsContainer>
      <Collapse in={expanded} timeout='auto' unmountOnExit>
        {errors.map((item) => (
          <Error>
            <strong>Field: {item.header}</strong> {item.message}
          </Error>
        ))}
      </Collapse>
    </>
  );
}
const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name Upload is required'),
});

export function RegistrationDataImport(): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [importType, setImportType] = useState();
  const [koboProject, setKoboProject] = useState();

  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [
    uploadMutate,
    { data: uploadData, loading: fileLoading },
  ] = useUploadImportDataXlsxFileMutation();
  const [
    createRegistrationXlsxMutate,
    { loading: createLoading },
  ] = useCreateRegistrationXlsxImportMutation();
  const [
    saveKoboImportDataMutate,
    { loading: saveKoboLoading, data: koboImportData },
  ] = useSaveKoboImportDataMutation();
  const [
    createRegistrationKoboMutate,
    { loading: createKoboLoading },
  ] = useCreateRegistrationKoboImportMutation();
  const { data: koboProjectsData, error, loading } = useAllKoboProjectsQuery({
    variables: { businessAreaSlug: businessArea },
  });
  const { t } = useTranslation();
  const xlsxErrors: UploadImportDataXlsxFileMutation['uploadImportDataXlsxFile']['errors'] = get(
    uploadData,
    'uploadImportDataXlsxFile.errors',
  );
  const koboErrors: SaveKoboImportDataMutation['saveKoboImportData']['errors'] =
    koboImportData?.saveKoboImportData?.errors;
  let counters = null;
  if (uploadData?.uploadImportDataXlsxFile?.importData) {
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
  if (koboImportData?.saveKoboImportData?.importData) {
    counters = (
      <>
        <div>
          {koboImportData?.saveKoboImportData?.importData.numberOfHouseholds}{' '}
          Households available to Import
        </div>
        <div>
          {koboImportData?.saveKoboImportData?.importData.numberOfIndividuals}{' '}
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
                businessAreaSlug: businessArea,
              },
            });
          }}
        />
        <Errors errors={xlsxErrors as XlsxRowErrorNode[]} />
      </>
    );
  } else if (importType === 'kobo') {
    const koboProjects = koboProjectsData?.allKoboProjects?.edges || [];
    importTypeSpecificContent = (
      <div>
        <FormControl variant='filled' margin='dense'>
          <InputLabel>Import from</InputLabel>
          <ComboBox
            value={koboProject}
            variant='filled'
            label='Kobo Project'
            onChange={(e) => {
              setKoboProject(e.target.value);
              saveKoboImportDataMutate({
                variables: {
                  projectId: e.target.value,
                  businessAreaSlug: businessArea,
                },
              });
            }}
            fullWidth
          >
            {koboProjects.map((item) => (
              <MenuItem key={item.node.id} value={item.node.id}>
                {item.node.name}
              </MenuItem>
            ))}
          </ComboBox>
        </FormControl>
        <ErrorsKobo errors={koboErrors as KoboErrorNode[]} />
      </div>
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
            let rdiId = null;
            if (importType === 'kobo') {
              const { data } = await createRegistrationKoboMutate({
                variables: {
                  registrationDataImportData: {
                    importDataId:
                      koboImportData.saveKoboImportData.importData.id,
                    name: values.name,
                    businessAreaSlug: businessArea,
                  },
                },
              });
              rdiId = data?.registrationKoboImport?.registrationDataImport?.id;
            } else if (importType === 'excel') {
              const { data } = await createRegistrationXlsxMutate({
                variables: {
                  registrationDataImportData: {
                    importDataId:
                      uploadData.uploadImportDataXlsxFile.importData.id,
                    name: values.name,
                    businessAreaSlug: businessArea,
                  },
                },
              });
              rdiId = data?.registrationXlsxImport?.registrationDataImport?.id;
            }

            showMessage('Registration', {
              pathname: `/${businessArea}/registration-data-import/${rdiId}`,
              historyMethod: 'push',
            });
          }}
          initialValues={{ name: '' }}
        >
          {({ submitForm }) => (
            <Form>
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  <Typography variant='h6'>
                    {t('Select File to Import')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                to CashAssist?
                <DialogDescription>
                  Are you sure you want to activate this Programme and push data
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
                  variant='filled'
                  component={FormikTextField}
                />
              </DialogContent>
              <StyledDialogFooter>
                <Button
                  variant='text'
                  color='primary'
                  component='a'
                  href='/api/download-template'
                >
                  DOWNLOAD TEMPLATE
                </Button>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>CANCEL</Button>
                  <Button
                    type='submit'
                    color='primary'
                    variant='contained'
                    disabled={
                      !uploadData ||
                      createLoading ||
                      saveKoboLoading ||
                      !koboImportData
                    }
                    onClick={() => {
                      submitForm();
                    }}
                  >
                    {t('IMPORT')}
                  </Button>
                </DialogActions>
              </StyledDialogFooter>
            </Form>
          )}
        </Formik>
      </Dialog>
    </span>
  );
}
