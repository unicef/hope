import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
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
} from '@mui/material';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { usePermissions } from '@hooks/usePermissions';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '@generated/graphql';
import { DropzoneField } from '@components/core/DropzoneField';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { uploadSupportingDocument } from '@api/paymentModuleApi';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface SupportingDocumentsSectionProps {
  initialOpen?: boolean;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const SupportingDocumentsSection = ({
  initialOpen = false,
  paymentPlan,
}: SupportingDocumentsSectionProps): React.ReactElement => {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const [documents, setDocuments] = useState(
    paymentPlan?.supportingDocuments || [],
  );
  const [fileToImport, setFileToImport] = useState(null);
  const [title, setTitle] = useState('');
  const [isExpanded, setIsExpanded] = useState(initialOpen);
  const [isLoading, setIsLoading] = useState(false);
  const [openImport, setOpenImport] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const canUploadFile = hasPermissions(
    PERMISSIONS.PM_UPLOAD_SUPPORTING_DOCUMENT,
    permissions,
  );
  const canRemoveFile = hasPermissions(
    PERMISSIONS.PM_DELETE_SUPPORTING_DOCUMENT,
    permissions,
  );
  const canDownloadFile = hasPermissions(
    PERMISSIONS.PM_DOWNLOAD_SUPPORTING_DOCUMENT,
    permissions,
  );

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      uploadSupportingDocument(businessArea, programId, paymentPlan.id, file),
    onSuccess: () => {
      setDocuments([
        ...documents,
        { id: Date.now().toString(), title, file: fileToImport },
      ]);
      setFileToImport(null);
      setTitle('');
      setIsLoading(false);
      setErrorMessage(null);
      showMessage(t('File uploaded successfully'));
    },
    onError: (err: Error) => {
      setErrorMessage(err.message);
      setIsLoading(false);
    },
  });

  const handleUpload = () => {
    if (!fileToImport || !title) {
      setErrorMessage(t('Please select a file and enter a title.'));
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

    uploadMutation.mutate(fileToImport, {
      onSuccess: () => {
        setDocuments([
          ...documents,
          {
            id: Date.now().toString(),
            title: fileToImport.name,
            file: fileToImport,
          },
        ]);
        setFileToImport(null);
        setIsLoading(false);
        setOpenImport(false);
        setErrorMessage('');
      },
      onError: (err) => {
        setErrorMessage(err ? err.message : t('File upload failed.'));
        setIsLoading(false);
      },
    });
  };

  const handleRemove = (id) => {
    setDocuments(documents.filter((doc) => doc.id !== id));
  };

  const handleDownload = (file) => {
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
        <Typography variant="h6">{t('Supporting Documents')}</Typography>
        <Box display="flex">
          {!isExpanded && canUploadFile && (
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
        <GreyText>{t('No documents uploaded')}</GreyText>
      )}

      <Collapse in={isExpanded}>
        {documents.map((doc) => (
          <div key={doc.id} data-cy="document-item">
            <Typography>{doc.title}</Typography>
            {canDownloadFile && (
              <IconButton
                onClick={() => handleDownload(doc.file)}
                data-cy="download-button"
              >
                <DownloadIcon />
              </IconButton>
            )}
            {canRemoveFile && (
              <IconButton
                onClick={() => handleRemove(doc.id)}
                data-cy="delete-button"
              >
                <DeleteIcon />
              </IconButton>
            )}
          </div>
        ))}
      </Collapse>
      {canUploadFile && (
        <Dialog
          open={openImport}
          onClose={() => setOpenImport(false)}
          scroll="paper"
          aria-labelledby="form-dialog-title"
        >
          <DialogTitleWrapper data-cy="dialog-import">
            <DialogTitle>{t('Select Files to Upload')}</DialogTitle>
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
              {errorMessage}
              <Grid container>
                <Grid item xs={12}>
                  <TextField
                    label={t('Title')}
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    fullWidth
                    margin="normal"
                    data-cy="title-input"
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
