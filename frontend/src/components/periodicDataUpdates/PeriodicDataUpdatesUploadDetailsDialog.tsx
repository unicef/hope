import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import { fetchPeriodicDataUpdateUploadDetails } from '@api/periodicDataUpdateApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';

interface PeriodicDataUpdatesUploadDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  uploadId: number;
}

// const StyledError = styled.p`
//   color: red;
// `;

const FormErrorDisplay = ({ formErrors }) => {
  if (!formErrors || !formErrors.length) {
    return null;
  }
  return (
    <div>
      {formErrors.map((error, index) => (
        <div key={index}>
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
export const PeriodicDataUpdatesUploadDetailsDialog: React.FC<
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
      fetchPeriodicDataUpdateUploadDetails(businessArea, programId, uploadId),
  });

  if (isLoading) return <LoadingComponent />;
  return (
    <Dialog open={open} onClose={onClose} scroll="paper">
      <DialogTitle>{t('Periodic Data Updates Errors')}</DialogTitle>
      <DialogContent>
        <NonFormErrorDisplay
          nonFormErrors={uploadDetailsData?.errors?.non_form_errors}
        />
        <FormErrorDisplay formErrors={uploadDetailsData?.errors?.form_errors} />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('Close')}</Button>
      </DialogActions>
    </Dialog>
  );
};
