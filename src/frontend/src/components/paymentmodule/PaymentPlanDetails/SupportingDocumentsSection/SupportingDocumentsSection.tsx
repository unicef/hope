import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import styled from 'styled-components';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import { PaperContainer } from '@components/targeting/PaperContainer';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { GreyText } from '@components/core/GreyText';
import { LoadingButton } from '@components/core/LoadingButton';
import {
  Typography,
  IconButton,
  Collapse,
  Dialog,
  DialogTitle,
  TextField,
  DialogActions,
  Button,
  Box,
  Grid,
  DialogContent,
  FormHelperText,
} from '@mui/material';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { usePermissions } from '@hooks/usePermissions';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery, PaymentPlanStatus } from '@generated/graphql';
import { DropzoneField } from '@components/core/DropzoneField';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import {
  deleteSupportingDocument,
  uploadSupportingDocument,
} from '@api/paymentModuleApi';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { GreyBox } from '@components/core/GreyBox';
import { BlueText } from '@components/grievances/LookUps/LookUpStyles';
import { useDownloadSupportingDocument } from './SupportingDocumentsSectionActions';

const StyledBox = styled(Box)`
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  background-color: ${({ theme }) => theme.palette.grey[200]};
  padding: 4px;
  margin-bottom: 4px;
`;

interface SupportingDocumentsSectionProps {
  initialOpen?: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const SupportingDocumentsSection = ({
  initialOpen = false,
  paymentPlan,
}: SupportingDocumentsSectionProps): React.ReactElement => {
  const permissions = usePermissions();
  const confirm = useConfirmation();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();

  const { mutate: downloadSupportingDocument } =
    useDownloadSupportingDocument();

  const { businessArea, programId } = useBaseUrl();
  const [documents, setDocuments] = useState(
    paymentPlan?.supportingDocuments || [],
  );
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [isExpanded, setIsExpanded] = useState(initialOpen);
  const [isLoading, setIsLoading] = useState(false);
  const [openImport, setOpenImport] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [titleError, setTitleError] = useState('');

  const canUploadFile =
    hasPermissions(PERMISSIONS.PM_UPLOAD_SUPPORTING_DOCUMENT, permissions) &&
    (paymentPlan.status === PaymentPlanStatus.Locked ||
      paymentPlan.status === PaymentPlanStatus.Open);

  const canRemoveFile =
    hasPermissions(PERMISSIONS.PM_DELETE_SUPPORTING_DOCUMENT, permissions) &&
    (paymentPlan.status === PaymentPlanStatus.Locked ||
      paymentPlan.status === PaymentPlanStatus.Open);

  const canDownloadFile = hasPermissions(
    PERMISSIONS.PM_DOWNLOAD_SUPPORTING_DOCUMENT,
    permissions,
  );

  const useUploadSupportingDocument = () => {
    return useMutation({
      mutationFn: ({
        _businessArea,
        _programId,
        paymentPlanId,
        file,
        _title,
      }: {
        _businessArea: string;
        _programId: string;
        paymentPlanId: string;
        file: File;
        _title: string;
      }) =>
        uploadSupportingDocument(
          _businessArea,
          _programId,
          paymentPlanId,
          file,
          _title,
        ),
      onSuccess: (doc) => {
        setFileToImport(null);
        setTitle('');
        setIsLoading(false);
        setErrorMessage('');
        showMessage(t('File uploaded successfully'));
        setOpenImport(false);
        setDocuments([
          ...documents,
          { id: doc.id, title: doc.title, file: doc.file },
        ]);
      },
      onError: (err: Error) => {
        setErrorMessage(err.message);
        setIsLoading(false);
      },
    });
  };

  const { mutate } = useUploadSupportingDocument();

  const handleUpload = (): void => {
    const maxFiles = 10;
    const currentFileCount = documents.length;

    if (currentFileCount >= maxFiles) {
      setErrorMessage(t('You cannot upload more than 10 files.'));
      return;
    }
    if (!fileToImport || !title) {
      setErrorMessage(t('Please select a file and enter a title.'));
      if (!title) {
        setTitleError(t('Title is required.'));
      }
      return;
    }
    if (fileToImport.size > 10 * 1024 * 1024) {
      setErrorMessage(t('File size must be ≤ 10MB.'));
      return;
    }
    const validExtensions = ['xlsx', 'pdf', 'jpg', 'jpeg', 'png'];
    const fileExtension = fileToImport.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !validExtensions.includes(fileExtension)) {
      setErrorMessage(t('Unsupported file type.'));
      return;
    }
    setIsLoading(true);
    mutate({
      _businessArea: businessArea,
      _programId: programId,
      paymentPlanId: paymentPlan.id,
      file: fileToImport,
      _title: title,
    });
  };

  const handleRemove = async (
    _businessArea: string,
    _programId: string,
    paymentPlanId: string,
    fileId: string,
  ) => {
    try {
      await deleteSupportingDocument(
        _businessArea,
        _programId,
        paymentPlanId,
        fileId,
      );
      setDocuments(documents.filter((doc) => doc.id !== fileId));
      showMessage(t('File deleted successfully.'));
    } catch (err) {
      setErrorMessage(
        t(`Failed to delete supporting document: ${err.message}`),
      );
    }
  };

  const confirmationModalTitle = t('Deleting Supporting Document');
  const confirmationText = t(
    'Are you sure you want to delete this file? This action cannot be reversed.',
  );

  const handleSupportingDocumentDownloadClick = (fileId: string) => {
    downloadSupportingDocument({
      businessAreaSlug: businessArea,
      programId,
      paymentPlanId: paymentPlan.id,
      fileId: fileId.toString(),
    });
  };

  const handleExpandClick = () => {
    setIsExpanded(!isExpanded);
  };

  const handleUploadClick = () => {
    setOpenImport(true);
  };

  return (
    <PaperContainer>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6" data-cy="supporting-documents-title">
          {t('Supporting Documents')}
        </Typography>
        <Box display="flex">
          {canUploadFile && (
            <Box mr={1}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleUploadClick}
                data-cy="upload-file-button"
              >
                {t('Upload File')}
              </Button>
            </Box>
          )}
          <Box>
            {documents.length > 0 && (
              <IconButton onClick={handleExpandClick} data-cy="expand-button">
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
          </Box>
        </Box>
      </Box>

      {documents.length === 0 && (
        <GreyText data-cy="supporting-documents-empty">
          {t('No documents uploaded')}
        </GreyText>
      )}

      <Collapse in={isExpanded}>
        <Box mt={2}>
          <Grid container spacing={3}>
            {documents.map((doc) => (
              <Grid key={doc.id} item xs={3}>
                <GreyBox p={3} key={doc.id} data-cy="document-item">
                  <Box
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Box display="flex" flexDirection="column">
                      <StyledBox>
                        <BlueText>{doc.title}</BlueText>
                      </StyledBox>
                      <StyledBox>
                        <BlueText>{doc.file}</BlueText>
                      </StyledBox>
                    </Box>
                    <Box>
                      {canDownloadFile && (
                        <IconButton
                          onClick={() =>
                            handleSupportingDocumentDownloadClick(doc.id)
                          }
                          data-cy="download-button"
                        >
                          <DownloadIcon />
                        </IconButton>
                      )}
                      {canRemoveFile && (
                        <IconButton
                          onClick={() =>
                            confirm({
                              title: confirmationModalTitle,
                              content: confirmationText,
                              type: 'error',
                            }).then(() =>
                              handleRemove(
                                businessArea,
                                programId,
                                paymentPlan.id,
                                doc.id,
                              ),
                            )
                          }
                        >
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </Box>
                </GreyBox>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Collapse>
      {canUploadFile && (
        <Dialog
          open={openImport}
          onClose={() => setOpenImport(false)}
          scroll="paper"
          aria-labelledby="form-dialog-title"
        >
          <DialogTitleWrapper data-cy="dialog-import">
            <DialogTitle>{t('Select File to Upload')}</DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <Box pb={2}>
              <GreyText>
                {t(
                  'The system accepts the following file extensions: XLSX, PDF, images (jpg, jpeg, png). File size must be ≤ 10MB.',
                )}
              </GreyText>
            </Box>
            <>
              <DropzoneField
                dontShowFilename={false}
                accepts={{
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    ['.xlsx'],
                  'application/pdf': ['.pdf'],
                  'image/jpeg': ['.jpeg', '.jpg'],
                  'image/png': ['.png'],
                }}
                loading={isLoading}
                onChange={(files) => {
                  if (files.length === 0) {
                    return;
                  }
                  const file = files[0];
                  const fileSizeMB = file.size / (1024 * 1024);
                  if (fileSizeMB > 200) {
                    setErrorMessage(
                      `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
                    );
                    return;
                  }

                  setFileToImport(file);
                }}
                data-cy="dropzone-field"
              />
              <FormHelperText error>{errorMessage}</FormHelperText>
              <Grid container>
                <Grid item xs={12}>
                  <TextField
                    size="small"
                    label={t('Title')}
                    value={title}
                    onChange={(e) => {
                      setTitle(e.target.value);
                      setTitleError('');
                    }}
                    fullWidth
                    margin="normal"
                    data-cy="title-input"
                    error={!!titleError}
                    helperText={titleError}
                  />
                </Grid>
              </Grid>
            </>
          </DialogContent>
          <DialogActions>
            <Button
              data-cy="close-button"
              onClick={() => {
                setOpenImport(false);
                setFileToImport(null);
                setErrorMessage('');
                setTitle('');
              }}
            >
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={isLoading}
              disabled={!fileToImport}
              type="submit"
              color="primary"
              variant="contained"
              onClick={handleUpload}
              data-cy="button-import-submit"
            >
              {t('Upload')}
            </LoadingButton>
          </DialogActions>
        </Dialog>
      )}
    </PaperContainer>
  );
};
