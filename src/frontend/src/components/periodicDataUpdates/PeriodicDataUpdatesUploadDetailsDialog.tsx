import React, { FC } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { RestService } from '@restgenerated/services/RestService';
import { PeriodicDataUpdateUploadDetail } from '@restgenerated/models/PeriodicDataUpdateUploadDetail';

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
  // Attempt to parse the JSON if it's a string; otherwise assume it's already an array
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
  const { data: uploadDetailsData, isLoading } =
    useQuery<PeriodicDataUpdateUploadDetail>({
      queryKey: [
        'periodicDataUpdateUploadDetails',
        businessArea,
        programId,
        uploadId,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPeriodicDataUpdateUploadsRetrieve({
          businessAreaSlug: businessArea,
          id: uploadId,
          programSlug: programId,
        }),
    });

  if (isLoading) return <LoadingComponent />;
  return (
    <Dialog open={open} onClose={onClose} scroll="paper">
      <DialogTitle>{t('Periodic Data Updates Errors')}</DialogTitle>
      <DialogContent>
        {/* //TODO: check if it is just errorsInfo */}
        <NonFormErrorDisplay nonFormErrors={uploadDetailsData?.errorsInfo} />
        <FormErrorDisplay formErrors={uploadDetailsData?.errorsInfo} />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('Close')}</Button>
      </DialogActions>
    </Dialog>
  );
};
