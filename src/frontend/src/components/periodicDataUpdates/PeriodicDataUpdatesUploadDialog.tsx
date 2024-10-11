import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';

import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from 'src/programContext';
import { useUploadPeriodicDataUpdateTemplate } from './PeriodicDataUpdatesTemplatesListActions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { GreyText } from '@components/core/GreyText';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

const UploadIcon = styled(Publish)`
  color: #043f91;
`;

const DisabledUploadIcon = styled(Publish)`
  color: #00000042;
`;

export const PeriodDataUpdatesUploadDialog = (): React.ReactElement => {
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const [open, setOpenImport] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const { isActiveProgram } = useProgramContext();
  const { t } = useTranslation();
  const { mutate, error } = useUploadPeriodicDataUpdateTemplate();
  const canPDUUpload = hasPermissions(PERMISSIONS.PDU_UPLOAD, permissions);

  const handleFileUpload = (): void => {
    if (fileToImport) {
      setIsLoading(true);
      const uploadData = {
        businessAreaSlug: businessArea,
        programId: programId,
        file: fileToImport,
        additionalParams: {},
      };

      mutate(uploadData, {
        onSuccess: () => {
          showMessage(t('File uploaded successfully'));
          setOpenImport(false);
          setFileToImport(null);
          setIsLoading(false);
        },
        onError: (uploadError) => {
          showMessage(
            uploadError ? uploadError.toString() : t('Error uploading file'),
          );
          setIsLoading(false);
        },
      });
    }
  };
  let errorMessage = null;
  if (error) {
    errorMessage = (
      <Error data-cy="pdu-upload-error">
        {t('Error uploading file:')} {error.message}
      </Error>
    );
  }

  return (
    <>
      <Box key="import">
        <ButtonTooltip
          startIcon={!isActiveProgram ? <DisabledUploadIcon /> : <UploadIcon />}
          color="primary"
          data-cy="button-import"
          onClick={() => setOpenImport(true)}
          disabled={!isActiveProgram || !canPDUUpload}
        >
          {t('Upload Data')}
        </ButtonTooltip>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper data-cy="dialog-import">
          <DialogTitle>
            <Box display="flex" flexDirection="column">
              {t('Select Files to Upload')}
              <GreyText>
                {t(
                  'The system accepts the following file extensions: XLSX, PDF, images (jpg, jpeg, png). File size must be \\u2264 10MB.',
                )}
              </GreyText>
            </Box>
          </DialogTitle>
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
                  showMessage(
                    `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
                  );
                  return;
                }

                setFileToImport(file);
              }}
            />
            {errorMessage}
          </>
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
              onClick={handleFileUpload}
              data-cy="button-import-submit"
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
};
