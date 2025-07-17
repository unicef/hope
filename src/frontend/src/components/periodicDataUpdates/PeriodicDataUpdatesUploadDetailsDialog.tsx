import { RestService } from '@restgenerated/services/RestService';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from '@mui/material';
import React, { FC } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';

interface PeriodicDataUpdatesUploadDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  uploadId: number;
}

const FormErrorDisplay = ({ formErrors }) => {
  if (!formErrors || !formErrors.length) {
    return null;
  }
  return (
    <div>
      {formErrors.map((error, index) => (
        <div key={index} data-cy="pdu-form-errors">
          <h3>Row: {error.row}</h3>
          <ul>
            {Object.entries(error.errors).map(([field, fieldErrors], idx) => (
              <li key={idx}>
                <strong>{field}</strong>
                {/*@ts-ignore*/}
                {fieldErrors.map((err, errIdx) => (
                  <div key={errIdx} style={{ color: 'red' }}>
                    {err.message}
                  </div>
                ))}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

const NonFormErrorDisplay = ({ nonFormErrors }) => {
  const errorMessages = nonFormErrors;

  if (!errorMessages || !errorMessages.length) {
    return null;
  }

  return (
    <div>
      {errorMessages.map((error, index) => (
        <p key={index} style={{ color: 'red' }}>
          {error}
        </p>
      ))}
    </div>
  );
};

export const PeriodicDataUpdatesUploadDetailsDialog: FC<
  PeriodicDataUpdatesUploadDetailsDialogProps
> = ({ open, onClose, uploadId }) => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { data: uploadDetailsData, isLoading } = useQuery({
    queryKey: [
      'periodicDataUpdateUploadDetails',
      businessArea,
      programId,
      uploadId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateUploadsRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: uploadId,
      }),
    enabled: !!uploadId,
  });

  if (isLoading) return <LoadingComponent />;
  return (
    <Dialog open={open} onClose={onClose} scroll="paper">
      <DialogTitle>{t('Periodic Data Updates Errors')}</DialogTitle>
      <DialogContent>
        {!uploadDetailsData?.errorsInfo ? (
          <Typography>No errors to display.</Typography>
        ) : (
          <>
            <NonFormErrorDisplay
              nonFormErrors={uploadDetailsData?.errorsInfo?.nonFormErrors}
            />
            <FormErrorDisplay
              formErrors={uploadDetailsData?.errorsInfo?.formErrors}
            />
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('Close')}</Button>
      </DialogActions>
    </Dialog>
  );
};
